#!/usr/bin/env node
//
// visual-diff-mcp — MCP server that lets LLMs SEE their HTML output
// by overlaying rendered HTML on reference images. The LLM gets visual
// feedback for the first time — not just code, but actual pixels.
//
// Tools:
//   render_overlay  — render HTML at N% opacity on top of a reference image
//   render_html      — just render HTML, get the screenshot
//   diff_images      — pixel difference between two images

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import puppeteer from "puppeteer";
import sharp from "sharp";
import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

let browser = null;

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: "new",
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });
  }
  return browser;
}

function fixRelativePaths(html, baseDir) {
  return html.replace(/(src|href)=["'](?!https?:\/\/|\/|data:)([^"']+)["']/g, (m, attr, path) => {
    const resolved = resolve(baseDir, path);
    return `${attr}="file://${resolved}"`;
  });
}

// ── render_html: HTML string → PNG screenshot buffer ──
async function renderToPng(html, width = 1440, height = 900, baseDir = __dirname) {
  const b = await getBrowser();
  const page = await b.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  const fixedHtml = fixRelativePaths(html, baseDir);
  await page.setContent(fixedHtml, { waitUntil: "networkidle0", timeout: 10000 });
  const png = await page.screenshot({ type: "png", fullPage: false });
  await page.close();
  return png;
}

// ── render_html: HTML string → PNG screenshot base64 ──
async function renderHtml(html, width = 1440, height = 900) {
  const png = await renderToPng(html, width, height);
  return { data: png.toString("base64"), mimeType: "image/png" };
}

// ── render_overlay: render HTML at opacity% on top of reference image ──
async function renderOverlay(html, referencePath, opacity = 50, width = 1440, height = 900) {
  const pref = resolve(referencePath);
  if (!existsSync(pref)) throw new Error(`Reference image not found: ${pref}`);
  const refBuf = readFileSync(pref);
  const ref = sharp(refBuf).resize(width, height, { fit: "contain", background: "#fff" });
  const htmlPng = await renderToPng(html, width, height);
  const composite = await sharp({ create: { width, height, channels: 4, background: "#fff" } })
    .composite([{ input: await ref.png().toBuffer() }, { input: htmlPng, blend: "over", opacity: opacity / 100 }])
    .png()
    .toBuffer();
  return { data: composite.toString("base64"), mimeType: "image/png" };
}

// ── diff_images: pixel diff between two images ──
async function diffImages(image1Path, image2Path, threshold = 10) {
  const p1 = resolve(image1Path);
  const p2 = resolve(image2Path);
  if (!existsSync(p1)) throw new Error(`Image 1 not found: ${p1}`);
  if (!existsSync(p2)) throw new Error(`Image 2 not found: ${p2}`);

  const [img1, img2] = await Promise.all([
    sharp(p1).resize(1440, 900, { fit: "contain" }).raw().toBuffer({ resolveWithObject: true }),
    sharp(p2).resize(1440, 900, { fit: "contain" }).raw().toBuffer({ resolveWithObject: true }),
  ]);

  const w = Math.min(img1.info.width, img2.info.width);
  const h = Math.min(img1.info.height, img2.info.height);
  const overlay = Buffer.alloc(w * h * 4);

  let totalDiff = 0;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const off = (y * w + x) * 4;
      const dr = Math.abs(img1.data[off] - img2.data[off]);
      const dg = Math.abs(img1.data[off + 1] - img2.data[off + 1]);
      const db = Math.abs(img1.data[off + 2] - img2.data[off + 2]);
      const diff = dr + dg + db;
      totalDiff += diff;

      if (diff > threshold) {
        overlay[off] = 255;
        overlay[off + 1] = 0;
        overlay[off + 2] = 0;
        overlay[off + 3] = 180;
      } else {
        overlay[off + 3] = 0;
      }
    }
  }

  const diffImg = await sharp(img1.data, { raw: { width: img1.info.width, height: img1.info.height, channels: 4 } })
    .composite([{ input: overlay, raw: { width: w, height: h, channels: 4 }, blend: "over" }])
    .png()
    .toBuffer();

  const percentDiff = (totalDiff / (w * h * 3 * 255)) * 100;
  return {
    data: diffImg.toString("base64"),
    mimeType: "image/png",
    diffPercent: Math.round(percentDiff * 100) / 100,
  };
}

// ── MCP Server ──
const server = new McpServer({
  name: "visual-diff-mcp",
  version: "1.0.0",
  description: "Render HTML over reference images so LLMs can visually compare and iterate design",
});

server.tool(
  "render_overlay",
  "Render HTML at X% opacity on top of a reference image. The LLM can SEE if its output matches the design visually. Returns a composite PNG image.",
  {
    html: z.string().describe("Full HTML document to render"),
    referencePath: z.string().describe("Absolute path to the reference design image (PNG/JPG)"),
    opacity: z.number().min(10).max(90).default(60).describe("Opacity of the HTML layer on top of reference (default 60 = reference mostly visible behind the output)"),
    width: z.number().default(1440).describe("Viewport width in pixels"),
    height: z.number().default(900).describe("Viewport height in pixels"),
  },
  async ({ html, referencePath, opacity, width, height }) => {
    try {
      const result = await renderOverlay(html, referencePath, opacity, width, height);
      return { content: [{ type: "image", data: result.data, mimeType: result.mimeType }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool(
  "render_html",
  "Render HTML and return a screenshot. Use this to SEE what your code actually produces.",
  {
    html: z.string().describe("Full HTML document to render"),
    width: z.number().default(1440).describe("Viewport width"),
    height: z.number().default(900).describe("Viewport height"),
  },
  async ({ html, width, height }) => {
    try {
      const result = await renderHtml(html, width, height);
      return { content: [{ type: "image", data: result.data, mimeType: result.mimeType }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool(
  "diff_images",
  "Pixel-diff two images. Highlights differences in red. Returns percentage of pixels that differ.",
  {
    image1: z.string().describe("Absolute path to first image"),
    image2: z.string().describe("Absolute path to second image"),
    threshold: z.number().min(1).max(100).default(10).describe("Pixel difference threshold (0-255 scale, higher = less sensitive)"),
  },
  async ({ image1, image2, threshold }) => {
    try {
      const result = await diffImages(image1, image2, threshold);
      return {
        content: [
          { type: "image", data: result.data, mimeType: result.mimeType },
          { type: "text", text: `Diff: ${result.diffPercent}% of pixels differ beyond threshold ${threshold}` },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// ── Start ──
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("visual-diff-mcp running — HTML rendering + overlay comparison tools ready");
