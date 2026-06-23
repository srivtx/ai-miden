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
import ImageTracer from "imagetracerjs";
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

// ── vectorize_region: crop a region of an image → convert to SVG paths ──
// Uses ImageTracer.js for local, dependency-free vectorization.
// Set `binarize: true` for high-contrast content (text, logos) — it forces
// 2 colors (black + background) for crisp results.
async function vectorizeRegion(imagePath, x, y, width, height, options = {}) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);

  // Optionally preprocess: upscale small regions, then optional binarize
  let pipe = sharp(absPath).extract({ left: x, top: y, width, height });
  if (options.binarize) {
    // Convert to grayscale, threshold to pure black/white
    pipe = pipe.greyscale().threshold(128);
  }
  const { data, info } = await pipe.raw().ensureAlpha().toBuffer({ resolveWithObject: true });

  const imgdata = { data: new Uint8ClampedArray(data), width: info.width, height: info.height };

  const tracerOptions = options.binarize
    ? {
        numberofcolors: 2,
        ltres: 1,
        qtres: 1,
        pathomit: 4,
        colorsampling: 2,
        colorquantcycles: 3,
        blurradius: 0,
        blurdelta: 0,
      }
    : {
        numberofcolors: 6,
        ltres: 1,
        qtres: 1,
        pathomit: 8,
        colorsampling: 2,
        colorquantcycles: 3,
        blurradius: 0,
        blurdelta: 0,
      };

  const svg = ImageTracer.imagedataToSVG(imgdata, tracerOptions);
  return { svg, width: info.width, height: info.height };
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
    .composite([
      { input: await ref.png().toBuffer() },
      { input: htmlPng, blend: "over", opacity: opacity / 100 },
    ])
    .png()
    .toBuffer();
  return { data: composite.toString("base64"), mimeType: "image/png" };
}

// ── diff_images: pixel diff between two images ──
async function diffImages(image1Path, image2Path, threshold = 10, width, height) {
  const p1 = resolve(image1Path);
  const p2 = resolve(image2Path);
  if (!existsSync(p1)) throw new Error(`Image 1 not found: ${p1}`);
  if (!existsSync(p2)) throw new Error(`Image 2 not found: ${p2}`);

  // Use provided dimensions OR auto-detect from first image
  let w = width,
    h = height;
  if (!w || !h) {
    const meta = await sharp(p1).metadata();
    w = w || meta.width;
    h = h || meta.height;
  }

  const [img1, img2] = await Promise.all([
    sharp(p1)
      .resize(w, h, { fit: "contain", background: "#fff" })
      .raw()
      .toBuffer({ resolveWithObject: true }),
    sharp(p2)
      .resize(w, h, { fit: "contain", background: "#fff" })
      .raw()
      .toBuffer({ resolveWithObject: true }),
  ]);

  const ww = Math.min(img1.info.width, img2.info.width);
  const hh = Math.min(img1.info.height, img2.info.height);
  const overlay = Buffer.alloc(ww * hh * 4);

  let totalDiff = 0;
  for (let y = 0; y < hh; y++) {
    for (let x = 0; x < ww; x++) {
      const off = (y * ww + x) * 4;
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

  const diffImg = await sharp(img1.data, {
    raw: { width: img1.info.width, height: img1.info.height, channels: 4 },
  })
    .composite([{ input: overlay, raw: { width: ww, height: hh, channels: 4 }, blend: "over" }])
    .png()
    .toBuffer();

  const percentDiff = (totalDiff / (ww * hh * 3 * 255)) * 100;
  return {
    data: diffImg.toString("base64"),
    mimeType: "image/png",
    diffPercent: Math.round(percentDiff * 100) / 100,
  };
}

// ── extract_palette: get the N most common colors in an image ──
async function extractPalette(imagePath, n = 10) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const { data, info } = await sharp(absPath).raw().toBuffer({ resolveWithObject: true });
  const counts = new Map();
  // Quantize to nearest 8 to merge near-identical colors
  for (let i = 0; i < data.length; i += info.channels) {
    const r = data[i] & 0xf8;
    const g = data[i + 1] & 0xf8;
    const b = data[i + 2] & 0xf8;
    const key = `${r},${g},${b}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  const total = data.length / info.channels;
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([k, c]) => {
      const [r, g, b] = k.split(",").map(Number);
      return {
        rgb: `rgb(${r},${g},${b})`,
        hex: "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join(""),
        count: c,
        percent: Math.round((c / total) * 10000) / 100,
      };
    });
}

// ── extract_elements: find distinct rectangular regions in an image ──
// Approach: downscale, find connected components of non-background pixels,
// merge nearby components, return bounding boxes.
async function extractElements(imagePath, options = {}) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const minSize = options.minSize || 200; // ignore regions smaller than this many px²
  const tolerance = options.tolerance || 30; // color distance to consider "same"
  const mergeGap = options.mergeGap || 10; // merge bboxes that are within this many px

  const { data, info } = await sharp(absPath).raw().toBuffer({ resolveWithObject: true });
  const { width: w, height: h, channels: c } = info;

  // Find background color (most common)
  const palette = await extractPalette(imagePath, 1);
  const bgR = parseInt(palette[0].rgb.match(/\d+/g)[0]);
  const bgG = parseInt(palette[0].rgb.match(/\d+/g)[1]);
  const bgB = parseInt(palette[0].rgb.match(/\d+/g)[2]);

  // Sample image into binary mask: 1 = element, 0 = background
  const mask = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * c;
      const dr = data[i] - bgR,
        dg = data[i + 1] - bgG,
        db = data[i + 2] - bgB;
      const dist = Math.sqrt(dr * dr + dg * dg + db * db);
      mask[y * w + x] = dist > tolerance ? 1 : 0;
    }
  }

  // Flood-fill connected components (4-connectivity)
  const visited = new Uint8Array(w * h);
  const components = [];
  const stack = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const idx = y * w + x;
      if (mask[idx] && !visited[idx]) {
        // BFS
        let minX = x,
          maxX = x,
          minY = y,
          maxY = y,
          count = 0;
        stack.push(idx);
        while (stack.length) {
          const cur = stack.pop();
          if (visited[cur]) continue;
          visited[cur] = 1;
          const cy = (cur / w) | 0;
          const cx = cur - cy * w;
          if (cx < minX) minX = cx;
          if (cx > maxX) maxX = cx;
          if (cy < minY) minY = cy;
          if (cy > maxY) maxY = cy;
          count++;
          // 4-neighbors
          if (cx > 0 && mask[cur - 1] && !visited[cur - 1]) stack.push(cur - 1);
          if (cx < w - 1 && mask[cur + 1] && !visited[cur + 1]) stack.push(cur + 1);
          if (cy > 0 && mask[cur - w] && !visited[cur - w]) stack.push(cur - w);
          if (cy < h - 1 && mask[cur + w] && !visited[cur + w]) stack.push(cur + w);
        }
        const area = (maxX - minX + 1) * (maxY - minY + 1);
        if (count >= minSize) {
          components.push({
            x: minX,
            y: minY,
            width: maxX - minX + 1,
            height: maxY - minY + 1,
            area,
            pixelCount: count,
          });
        }
      }
    }
  }

  // Merge overlapping/nearby components
  components.sort((a, b) => b.area - a.area);
  const merged = [];
  for (const c of components) {
    let didMerge = false;
    for (const m of merged) {
      const horizOverlap = c.x < m.x + m.width + mergeGap && c.x + c.width + mergeGap > m.x;
      const vertOverlap = c.y < m.y + m.height + mergeGap && c.y + c.height + mergeGap > m.y;
      if (horizOverlap && vertOverlap) {
        const nx = Math.min(c.x, m.x);
        const ny = Math.min(c.y, m.y);
        const nw = Math.max(c.x + c.width, m.x + m.width) - nx;
        const nh = Math.max(c.y + c.height, m.y + m.height) - ny;
        m.x = nx;
        m.y = ny;
        m.width = nw;
        m.height = nh;
        m.area = nw * nh;
        m.pixelCount += c.pixelCount;
        didMerge = true;
        break;
      }
    }
    if (!didMerge) merged.push({ ...c });
  }

  // Sort by y then x for readable output
  merged.sort((a, b) => a.y - b.y || a.x - b.x);

  // Classify: full-width rows are "strips", smaller are "elements"
  for (const m of merged) {
    if (m.width > w * 0.7) m.type = "strip";
    else if (m.area > 50000) m.type = "region";
    else m.type = "element";
  }

  return {
    backgroundColor: palette[0].hex,
    imageSize: { width: w, height: h },
    elementCount: merged.length,
    elements: merged,
  };
}

// ── find_text_regions: detect text-like horizontal regions ──
// Text has high horizontal edge density. We compute horizontal Sobel-like
// gradient, then find rows/columns with high density → text bands.
async function findTextRegions(imagePath, options = {}) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const minHeight = options.minHeight || 12; // minimum text band height
  const maxHeight = options.maxHeight || 200; // maximum (anything taller is probably a panel)
  const minWidth = options.minWidth || 30; // minimum text band width
  const edgeThreshold = options.edgeThreshold || 40; // brightness jump

  const { data, info } = await sharp(absPath)
    .greyscale()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const { width: w, height: h } = info;

  // For each row, count "edge pixels" (large horizontal jump)
  const rowEdgeCount = new Uint32Array(h);
  for (let y = 0; y < h; y++) {
    let count = 0;
    for (let x = 1; x < w; x++) {
      if (Math.abs(data[y * w + x] - data[y * w + x - 1]) > edgeThreshold) count++;
    }
    rowEdgeCount[y] = count;
  }

  // Threshold: a row is "text-like" if it has many edges
  const edgeMedian = [...rowEdgeCount].sort((a, b) => a - b)[Math.floor(h / 2)];
  const rowIsText = new Uint8Array(h);
  const textThreshold = Math.max(edgeMedian * 3, 5);
  for (let y = 0; y < h; y++) {
    rowIsText[y] = rowEdgeCount[y] > textThreshold ? 1 : 0;
  }

  // Find vertical bands of text-like rows
  const bands = [];
  let inBand = false,
    bandStart = 0;
  for (let y = 0; y < h; y++) {
    if (rowIsText[y] && !inBand) {
      inBand = true;
      bandStart = y;
    } else if (!rowIsText[y] && inBand) {
      inBand = false;
      const height = y - bandStart;
      if (height >= minHeight && height <= maxHeight) {
        // For each band, find the horizontal extent of text
        let minX = w,
          maxX = 0;
        for (let yy = bandStart; yy < y; yy++) {
          for (let x = 0; x < w; x++) {
            if (data[yy * w + x] !== data[Math.min(yy, h - 1) * w + x]) {
              // skip
            }
            if (Math.abs(data[yy * w + x] - data[yy * w + (x ? x - 1 : 0)]) > edgeThreshold) {
              if (x < minX) minX = x;
              if (x > maxX) maxX = x;
            }
          }
        }
        const width = maxX - minX;
        if (width >= minWidth) {
          bands.push({ x: minX, y: bandStart, width, height });
        }
      }
    }
  }

  return {
    imageSize: { width: w, height: h },
    textRegionCount: bands.length,
    textRegions: bands,
  };
}

// ── crop_with_transparency: crop a region and make bg color transparent ──
// The killer tool. Lets you stamp any element from a reference image into
// HTML without bringing the background. E.g. crop the ASTRAL logo, knock out
// the cream bg → drop into HTML as a transparent PNG.
async function cropWithTransparency(imagePath, x, y, width, height, options = {}) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const tolerance = options.tolerance ?? 30;
  // Auto-detect bg if not given: sample the corners
  let bg = options.backgroundColor;
  if (!bg) {
    const { data, info } = await sharp(absPath).raw().toBuffer({ resolveWithObject: true });
    const c = info.channels;
    const samples = [
      [0, 0],
      [info.width - 1, 0],
      [0, info.height - 1],
      [info.width - 1, info.height - 1],
    ];
    const colors = samples.map(([sx, sy]) => {
      const i = (sy * info.width + sx) * c;
      return [data[i], data[i + 1], data[i + 2]];
    });
    // Take the most common corner color
    const keyOf = (c) => `${c[0]},${c[1]},${c[2]}`;
    const counts = new Map();
    for (const cc of colors) counts.set(keyOf(cc), (counts.get(keyOf(cc)) || 0) + 1);
    const top = [...counts.entries()]
      .sort((a, b) => b[1] - a[1])[0][0]
      .split(",")
      .map(Number);
    bg = { r: top[0], g: top[1], b: top[2] };
  } else {
    const m = bg.match(/^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (m) bg = { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) };
    else {
      const m2 = bg.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (m2) bg = { r: +m2[1], g: +m2[2], b: +m2[3] };
    }
  }

  // Build the cropped image with bg color → transparent
  const { data, info } = await sharp(absPath)
    .extract({ left: x, top: y, width, height })
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const out = Buffer.from(data);
  for (let i = 0; i < data.length; i += 4) {
    const dr = data[i] - bg.r,
      dg = data[i + 1] - bg.g,
      db = data[i + 2] - bg.b;
    const dist = Math.sqrt(dr * dr + dg * dg + db * db);
    if (dist < tolerance) {
      out[i + 3] = 0; // transparent
    } else if (dist < tolerance * 2) {
      // Soft edge: partial alpha
      out[i + 3] = Math.max(0, Math.min(255, Math.round(((dist - tolerance) / tolerance) * 255)));
    }
  }

  const png = await sharp(out, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png()
    .toBuffer();
  return { png, width: info.width, height: info.height, backgroundColor: bg };
}

// ── read_text: OCR using tesseract.js ──
// Reads text from an image, optionally bounded to a region. Returns the
// text + per-word bounding boxes so you can see WHERE each word is.
async function readText(imagePath, x, y, width, height) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const Tesseract = (await import("tesseract.js")).default;
  let imgBuf;
  if (x !== undefined) {
    imgBuf = await sharp(absPath).extract({ left: x, top: y, width, height }).png().toBuffer();
  } else {
    imgBuf = await sharp(absPath).png().toBuffer();
  }
  const { data } = await Tesseract.recognize(imgBuf, "eng");
  return {
    text: data.text.trim(),
    words: data.words.map((w) => ({
      text: w.text,
      confidence: Math.round(w.confidence),
      bbox: { x: w.bbox.x0, y: w.bbox.y0, w: w.bbox.x1 - w.bbox.x0, h: w.bbox.y1 - w.bbox.y0 },
    })),
  };
}

// ── sample_color: get the exact RGB at a specific pixel ──
// Trivial but crucial: when you need to know the EXACT color of a single
// pixel (border, icon stroke, etc.) without parsing a palette.
async function sampleColor(imagePath, x, y) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const { data, info } = await sharp(absPath).raw().toBuffer({ resolveWithObject: true });
  const i = (y * info.width + x) * info.channels;
  const r = data[i],
    g = data[i + 1],
    b = data[i + 2];
  const hex = "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("");
  return { r, g, b, hex, rgb: `rgb(${r},${g},${b})` };
}

// ── analyze_font: detect font features from a cropped text image ──
// Heuristics: detect serif vs sans-serif, weight (light/regular/bold/black),
// x-height ratio, stroke contrast, and suggest matching web fonts.
// This is a local heuristic — not a font identifier, but it gives the
// LLM enough signal to pick a Google Font that approximates.
async function analyzeFont(imagePath, x, y, width, height) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const { data, info } = await sharp(absPath)
    .extract({ left: x, top: y, width, height })
    .greyscale()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const w = info.width,
    h = info.height;

  // Find dark text pixels (assume text is dark on light bg)
  const threshold = 100;
  const isText = new Uint8Array(w * h);
  for (let i = 0; i < data.length; i++) isText[i] = data[i] < threshold ? 1 : 0;

  // Find text bounds (rows that contain text)
  let textTop = h,
    textBottom = 0,
    textLeft = w,
    textRight = 0;
  for (let y2 = 0; y2 < h; y2++) {
    for (let x2 = 0; x2 < w; x2++) {
      if (isText[y2 * w + x2]) {
        if (y2 < textTop) textTop = y2;
        if (y2 > textBottom) textBottom = y2;
        if (x2 < textLeft) textLeft = x2;
        if (x2 > textRight) textRight = x2;
      }
    }
  }
  if (textBottom === 0) return { error: "no text detected" };

  const capHeight = textBottom - textTop + 1;
  const textWidth = textRight - textLeft + 1;

  // Detect x-height: find a horizontal line where text density is high
  // (the x-height band is in the middle of lowercase letters)
  const rowDensity = new Uint32Array(h);
  for (let y2 = textTop; y2 <= textBottom; y2++) {
    for (let x2 = textLeft; x2 <= textRight; x2++) {
      if (isText[y2 * w + x2]) rowDensity[y2]++;
    }
  }
  // Find the most dense row in the middle portion (x-height is at ~50% of cap height)
  const midStart = textTop + Math.floor(capHeight * 0.4);
  const midEnd = textTop + Math.floor(capHeight * 0.7);
  let xHeightRow = midStart,
    maxDensity = 0;
  for (let y2 = midStart; y2 <= midEnd; y2++) {
    if (rowDensity[y2] > maxDensity) {
      maxDensity = rowDensity[y2];
      xHeightRow = y2;
    }
  }
  // Approximate x-height as band around the densest middle row
  let xHeightTop = xHeightRow,
    xHeightBottom = xHeightRow;
  for (let y2 = xHeightRow; y2 >= textTop; y2--) {
    if (rowDensity[y2] < maxDensity * 0.5) break;
    xHeightTop = y2;
  }
  for (let y2 = xHeightRow; y2 <= textBottom; y2++) {
    if (rowDensity[y2] < maxDensity * 0.5) break;
    xHeightBottom = y2;
  }
  const xHeight = xHeightBottom - xHeightTop + 1;
  const xHeightRatio = xHeight / capHeight;

  // Detect stroke width: average run length of horizontal black runs in x-height band
  let totalRun = 0,
    runCount = 0;
  for (let y2 = xHeightTop; y2 <= xHeightBottom; y2++) {
    let run = 0;
    for (let x2 = textLeft; x2 <= textRight; x2++) {
      if (isText[y2 * w + x2]) run++;
      else {
        if (run > 0) {
          totalRun += run;
          runCount++;
        }
        run = 0;
      }
    }
    if (run > 0) {
      totalRun += run;
      runCount++;
    }
  }
  const strokeWidth = runCount > 0 ? totalRun / runCount : 0;
  const strokeRatio = strokeWidth / capHeight;

  // Detect serifs: look for abrupt width changes at top/bottom of strokes
  // (Simplified: check if any column in the cap-height range has text at the very top AND very bottom)
  let serifIndicator = 0;
  for (let x2 = textLeft; x2 <= textRight; x2++) {
    let topHasText = false,
      bottomHasText = false;
    for (let y2 = textTop; y2 < textTop + 3; y2++) if (isText[y2 * w + x2]) topHasText = true;
    for (let y2 = textBottom - 2; y2 <= textBottom; y2++)
      if (isText[y2 * w + x2]) bottomHasText = true;
    if (topHasText && bottomHasText) serifIndicator++;
  }
  const serifRatio = serifIndicator / textWidth;
  const hasSerifs = serifRatio > 0.3;

  // Classify weight
  let weight;
  if (strokeRatio > 0.18) weight = "black";
  else if (strokeRatio > 0.12) weight = "bold";
  else if (strokeRatio > 0.07) weight = "regular";
  else weight = "light";

  // Suggest matching web fonts
  const suggestions = [];
  if (hasSerifs) {
    suggestions.push("'Playfair Display'", "'Lora'", "'EB Garamond'");
  } else {
    if (weight === "black" || weight === "bold") {
      suggestions.push("'Inter'", "'Geist'", "'Manrope'");
    } else {
      suggestions.push("'Inter'", "'Geist'", "'Plus Jakarta Sans'");
    }
  }

  return {
    capHeightPx: capHeight,
    xHeightPx: xHeight,
    xHeightRatio: Math.round(xHeightRatio * 100) / 100,
    strokeRatio: Math.round(strokeRatio * 100) / 100,
    hasSerifs,
    weight,
    suggestedWebFonts: suggestions,
    note: "Heuristic only. For pixel-perfect match, crop the text from the reference and use it as an image stamp (see crop_with_transparency).",
  };
}

// ── match_region: find the best match of a region (from image A) inside image B ──
// Uses simple template matching with sum-of-absolute-differences.
// Useful for tracking where an element from the reference ended up in your render.
async function matchRegion(imagePath, templatePath, x, y, width, height) {
  const p1 = resolve(imagePath);
  const p2 = resolve(templatePath);
  if (!existsSync(p1)) throw new Error(`Image not found: ${p1}`);
  if (!existsSync(p2)) throw new Error(`Template not found: ${p2}`);

  const [big, small] = await Promise.all([
    sharp(p1).greyscale().raw().toBuffer({ resolveWithObject: true }),
    sharp(p2)
      .extract({ left: x, top: y, width, height })
      .greyscale()
      .raw()
      .toBuffer({ resolveWithObject: true }),
  ]);

  const bigW = big.info.width,
    bigH = big.info.height;
  const smallW = small.info.width,
    smallH = small.info.height;

  if (smallW > bigW || smallH > bigH) {
    throw new Error("Template larger than image");
  }

  // Slide template over image, compute SAD at each position
  let bestX = 0,
    bestY = 0,
    bestSAD = Infinity;
  const stride = 4; // sample every 4 pixels for speed; refine later
  for (let yy = 0; yy <= bigH - smallH; yy += stride) {
    for (let xx = 0; xx <= bigW - smallW; xx += stride) {
      let sad = 0;
      for (let sy = 0; sy < smallH; sy += 2) {
        for (let sx = 0; sx < smallW; sx += 2) {
          const bi = (yy + sy) * bigW + (xx + sx);
          const si = sy * smallW + sx;
          sad += Math.abs(big.data[bi] - small.data[si]);
        }
      }
      if (sad < bestSAD) {
        bestSAD = sad;
        bestX = xx;
        bestY = yy;
      }
    }
  }

  // Refine around the best coarse position
  for (let yy = Math.max(0, bestY - stride); yy <= Math.min(bigH - smallH, bestY + stride); yy++) {
    for (
      let xx = Math.max(0, bestX - stride);
      xx <= Math.min(bigW - smallW, bestX + stride);
      xx++
    ) {
      let sad = 0;
      for (let sy = 0; sy < smallH; sy++) {
        for (let sx = 0; sx < smallW; sx++) {
          const bi = (yy + sy) * bigW + (xx + sx);
          const si = sy * smallW + sx;
          sad += Math.abs(big.data[bi] - small.data[si]);
        }
      }
      if (sad < bestSAD) {
        bestSAD = sad;
        bestX = xx;
        bestY = yy;
      }
    }
  }

  // Compute similarity (lower SAD = higher similarity)
  const maxSAD = smallW * smallH * 255;
  const similarity = Math.max(0, Math.round((1 - bestSAD / maxSAD) * 10000) / 100);

  return {
    found: { x: bestX, y: bestY, width: smallW, height: smallH },
    similarity,
    sadScore: bestSAD,
  };
}

// ── fit_to_view: render HTML at a size that fits in a target viewport ──
// Maintains the reference's aspect ratio so things don't cramp or distort.
// Default target is 1440x900 (typical browser viewport).
async function fitToView(html, referencePath, maxWidth = 1440, maxHeight = 900) {
  const pref = resolve(referencePath);
  if (!existsSync(pref)) throw new Error(`Reference image not found: ${pref}`);
  const meta = await sharp(pref).metadata();
  const refW = meta.width,
    refH = meta.height;
  const refAspect = refW / refH;
  const viewAspect = maxWidth / maxHeight;
  let renderW, renderH;
  if (refAspect > viewAspect) {
    renderW = maxWidth;
    renderH = Math.round(maxWidth / refAspect);
  } else {
    renderH = maxHeight;
    renderW = Math.round(maxHeight * refAspect);
  }
  return await renderHtml(html, renderW, renderH);
}

// ── render_states: render HTML in default + multiple hover/focus states ──
// Useful for verifying interactive elements. Returns a single composite image
// with the page in each state, labeled.
async function renderStates(html, width = 1440, height = 900, states = null) {
  const defaultStates = states || [
    { name: "default", hover: null },
    { name: "hover-banner", hover: ".banner a" },
    { name: "hover-cta", hover: ".ctas .btn-primary" },
    { name: "hover-secondary", hover: ".ctas .btn-secondary" },
    { name: "hover-nav", hover: ".nav-links a" },
    { name: "hover-icon", hover: ".icon-btn" },
  ];
  const b = await getBrowser();
  const page = await b.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.setContent(fixRelativePaths(html, __dirname), {
    waitUntil: "networkidle0",
    timeout: 10000,
  });
  await new Promise((r) => setTimeout(r, 300));

  const shots = [];
  for (const s of defaultStates) {
    if (s.hover) {
      try {
        await page.hover(s.hover);
      } catch (e) {
        /* selector not found */
      }
      await new Promise((r) => setTimeout(r, 200));
    } else {
      // Move mouse to corner to ensure no hover
      await page.mouse.move(0, 0);
      await new Promise((r) => setTimeout(r, 100));
    }
    const png = await page.screenshot({ type: "png" });
    shots.push({ name: s.name, png });
  }
  await page.close();

  // Compose: stack vertically with labels
  const labelH = 40;
  const totalH = (height + labelH) * shots.length;
  const composite = sharp({
    create: { width, height: totalH, channels: 4, background: { r: 20, g: 20, b: 30, alpha: 1 } },
  });
  const inputs = [];
  for (let i = 0; i < shots.length; i++) {
    const y = i * (height + labelH);
    // Label as SVG
    const labelSvg = `<svg width="${width}" height="${labelH}" xmlns="http://www.w3.org/2000/svg">
      <rect width="${width}" height="${labelH}" fill="#1a1a2a"/>
      <text x="20" y="28" font-family="monospace" font-size="18" fill="#5e6ad2">[${i}] ${shots[i].name}</text>
    </svg>`;
    inputs.push({ input: Buffer.from(labelSvg), top: y, left: 0 });
    inputs.push({ input: shots[i].png, top: y + labelH, left: 0 });
  }
  const out = await composite.composite(inputs).png().toBuffer();
  return { data: out.toString("base64"), mimeType: "image/png", stateCount: shots.length };
}

// ── classify_element: tell you if a crop is "text" (CSS+font) or "stamp" ──
// Heuristics:
//   - colorCount (after quantization): text = 1-2, icons/logos = 2-5, art = 5+
//   - aspectRatio: very wide/short = text label
//   - colorComplexity: high variance = stamp-worthy
//   - solidRunLength: long horizontal runs = text
// Returns: { kind, suggestedApproach, confidence }
async function classifyElement(imagePath, x, y, width, height) {
  const absPath = resolve(imagePath);
  if (!existsSync(absPath)) throw new Error(`Image not found: ${absPath}`);
  const { data, info } = await sharp(absPath)
    .extract({ left: x, top: y, width, height })
    .raw()
    .toBuffer({ resolveWithObject: true });
  const w = info.width,
    h = info.height,
    c = info.channels;

  // Count distinct colors (quantized to nearest 16)
  const colorSet = new Set();
  for (let i = 0; i < data.length; i += c) {
    const r = data[i] & 0xf0,
      g = data[i + 1] & 0xf0,
      b = data[i + 2] & 0xf0;
    colorSet.add(`${r},${g},${b}`);
  }
  const colorCount = colorSet.size;

  // Aspect ratio
  const aspect = w / h;

  // Color complexity: std dev of all pixel values
  let sum = 0,
    sumSq = 0,
    n = 0;
  for (let i = 0; i < data.length; i += c) {
    const v = (data[i] + data[i + 1] + data[i + 2]) / 3;
    sum += v;
    sumSq += v * v;
    n++;
  }
  const mean = sum / n;
  const stddev = Math.sqrt(sumSq / n - mean * mean);

  // Longest solid horizontal run (rows of single color = text or background)
  let maxRun = 0;
  let run = 1;
  for (let y2 = 0; y2 < h; y2++) {
    for (let x2 = 1; x2 < w; x2++) {
      const i1 = (y2 * w + x2 - 1) * c;
      const i2 = (y2 * w + x2) * c;
      if (
        Math.abs(data[i1] - data[i2]) < 10 &&
        Math.abs(data[i1 + 1] - data[i2 + 1]) < 10 &&
        Math.abs(data[i1 + 2] - data[i2 + 2]) < 10
      ) {
        run++;
      } else {
        if (run > maxRun) maxRun = run;
        run = 1;
      }
    }
  }
  if (run > maxRun) maxRun = run;
  const runRatio = maxRun / w;

  // Heuristic classification
  let kind, approach, confidence;
  if (colorCount <= 2 && aspect > 2) {
    kind = "text";
    approach =
      "Use CSS with a web font. Set color to the dark pixel value. Common font matches: Inter, Geist, Plus Jakarta Sans.";
    confidence = 0.9;
  } else if (colorCount <= 2 && aspect <= 2) {
    kind = "icon";
    approach =
      "Use an inline SVG. If complex (curves, gradients), use crop_with_transparency to extract a transparent PNG.";
    confidence = 0.75;
  } else if (colorCount <= 5 && stddev < 50) {
    kind = "simple-graphic";
    approach =
      "CSS or simple inline SVG with fill colors. Few enough colors to recreate with CSS gradients or solid shapes.";
    confidence = 0.7;
  } else {
    kind = "stamp";
    approach =
      "Use crop_with_transparency to extract a transparent PNG and embed as <img>. Don't try to recreate — pixel art, custom fonts, or complex illustrations can't be reproduced with CSS.";
    confidence = 0.85;
  }

  return {
    kind,
    approach,
    confidence,
    metrics: {
      colorCount,
      aspectRatio: Math.round(aspect * 100) / 100,
      colorStddev: Math.round(stddev * 10) / 10,
      longestSolidRunRatio: Math.round(runRatio * 100) / 100,
    },
  };
}

// ── MCP Server ──
const server = new McpServer({
  name: "visual-diff-mcp",
  version: "1.5.0",
  description: "Render HTML over reference images so LLMs can visually compare and iterate design",
});

server.tool(
  "render_overlay",
  "Render HTML at X% opacity on top of a reference image. The LLM can SEE if its output matches the design visually. Returns a composite PNG image.",
  {
    html: z.string().describe("Full HTML document to render"),
    referencePath: z.string().describe("Absolute path to the reference design image (PNG/JPG)"),
    opacity: z
      .number()
      .min(10)
      .max(90)
      .default(60)
      .describe(
        "Opacity of the HTML layer on top of reference (default 60 = reference mostly visible behind the output)",
      ),
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
  },
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
  },
);

server.tool(
  "vectorize_region",
  "Crop a region of an image and convert it to SVG paths. Use this for logos, custom fonts, and illustrations that can't be reproduced with CSS. Set binarize=true for high-contrast text/logos for crisp black-on-white output.",
  {
    imagePath: z.string().describe("Absolute path to the source image"),
    x: z.number().describe("Left edge of the crop region in pixels"),
    y: z.number().describe("Top edge of the crop region in pixels"),
    width: z.number().describe("Crop width in pixels"),
    height: z.number().describe("Crop height in pixels"),
    binarize: z
      .boolean()
      .default(false)
      .describe("If true, convert to pure black-on-white first (best for text/logos)"),
  },
  async ({ imagePath, x, y, width, height, binarize }) => {
    try {
      const result = await vectorizeRegion(imagePath, x, y, width, height, { binarize });
      return {
        content: [
          {
            type: "text",
            text: `SVG (${result.width}x${result.height}):\n${result.svg}\n\nEmbed with: <svg width="${result.width}" height="${result.height}" viewBox="0 0 ${result.width} ${result.height}">${result.svg}</svg>`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "diff_images",
  "Pixel-diff two images. Highlights differences in red. Returns percentage of pixels that differ.",
  {
    image1: z.string().describe("Absolute path to first image"),
    image2: z.string().describe("Absolute path to second image"),
    threshold: z
      .number()
      .min(1)
      .max(100)
      .default(10)
      .describe("Pixel difference threshold (0-255 scale, higher = less sensitive)"),
    width: z
      .number()
      .optional()
      .describe("Resize both to this width before diffing (default: image1's natural size)"),
    height: z
      .number()
      .optional()
      .describe("Resize both to this height before diffing (default: image1's natural size)"),
  },
  async ({ image1, image2, threshold, width, height }) => {
    try {
      const result = await diffImages(image1, image2, threshold, width, height);
      return {
        content: [
          { type: "image", data: result.data, mimeType: result.mimeType },
          {
            type: "text",
            text: `Diff: ${result.diffPercent}% of pixels differ beyond threshold ${threshold}`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "extract_palette",
  "Get the N most common colors in an image, with hex codes and percentage of total pixels. Use this to find the exact colors of a design (background, brand, accent).",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    n: z.number().min(1).max(50).default(10).describe("Number of colors to return"),
  },
  async ({ imagePath, n }) => {
    try {
      const palette = await extractPalette(imagePath, n);
      const text = palette.map((p) => `${p.hex} (${p.rgb}) - ${p.percent}%`).join("\n");
      return { content: [{ type: "text", text: `Top ${n} colors:\n${text}` }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "extract_elements",
  "Find distinct rectangular regions in an image (logo, nav, hero, buttons, panels, etc.) and return their bounding boxes. Detects non-background regions via flood-fill, merges nearby ones. Use this to know exactly where to position each HTML element or where to crop a reference stamp.",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    minSize: z.number().default(200).describe("Ignore regions with fewer than this many pixels"),
    tolerance: z
      .number()
      .min(5)
      .max(100)
      .default(30)
      .describe("Color distance from background to consider as 'element'"),
    mergeGap: z
      .number()
      .min(0)
      .max(50)
      .default(10)
      .describe("Merge regions that are within this many pixels of each other"),
  },
  async ({ imagePath, minSize, tolerance, mergeGap }) => {
    try {
      const result = await extractElements(imagePath, { minSize, tolerance, mergeGap });
      const elText = result.elements
        .map(
          (e, i) =>
            `  [${i}] ${e.type}  x=${e.x} y=${e.y} w=${e.width} h=${e.height}  area=${e.area}`,
        )
        .join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Background: ${result.backgroundColor}\nImage: ${result.imageSize.width}x${result.imageSize.height}\nFound ${result.elementCount} elements:\n${elText}`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "find_text_regions",
  "Detect text-like horizontal regions in an image and return their bounding boxes. Text has high horizontal edge density, so this finds rows with many vertical strokes and groups them into bands. Use this to know where text is so you can target a font match or crop a stamp.",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    minHeight: z.number().default(12).describe("Minimum text band height in pixels"),
    maxHeight: z
      .number()
      .default(200)
      .describe("Maximum text band height (taller = probably a panel)"),
    minWidth: z.number().default(30).describe("Minimum text band width in pixels"),
  },
  async ({ imagePath, minHeight, maxHeight, minWidth }) => {
    try {
      const result = await findTextRegions(imagePath, { minHeight, maxHeight, minWidth });
      const tText = result.textRegions
        .map((t, i) => `  [${i}] text  x=${t.x} y=${t.y} w=${t.width} h=${t.height}`)
        .join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Image: ${result.imageSize.width}x${result.imageSize.height}\nFound ${result.textRegionCount} text regions:\n${tText}`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "crop_with_transparency",
  "Crop a region of an image and make the background color (or any specified color) transparent. Returns a PNG with alpha channel — drop straight into HTML with no bg bleed. THIS is the tool for stamping elements from a reference image into your HTML.",
  {
    imagePath: z.string().describe("Absolute path to the source image"),
    x: z.number().describe("Left edge of the crop region in pixels"),
    y: z.number().describe("Top edge of the crop region in pixels"),
    width: z.number().describe("Crop width in pixels"),
    height: z.number().describe("Crop height in pixels"),
    backgroundColor: z
      .string()
      .optional()
      .describe(
        "Color to knock out (hex like '#f4f4f1' or 'rgb(244,244,241)'). If omitted, uses the most common corner color.",
      ),
    tolerance: z
      .number()
      .min(0)
      .max(100)
      .default(30)
      .describe("Color distance threshold for transparency (0 = strict, 100 = loose)"),
  },
  async ({ imagePath, x, y, width, height, backgroundColor, tolerance }) => {
    try {
      const result = await cropWithTransparency(imagePath, x, y, width, height, {
        backgroundColor,
        tolerance,
      });
      return {
        content: [
          { type: "image", data: result.png.toString("base64"), mimeType: "image/png" },
          {
            type: "text",
            text: `Cropped ${result.width}x${result.height} with bg ${JSON.stringify(result.backgroundColor)} knocked out. Save the PNG and reference it in HTML as <img src="cropped.png"> — it composites cleanly over any background.`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "read_text",
  "OCR — extract text from an image (or a region of it) using Tesseract. Returns the recognized text plus per-word bounding boxes so you know WHERE each word is. Use this to read the actual text in a reference image so you can write the right copy in your HTML.",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    x: z.number().optional().describe("Left edge of region to OCR (default: full image)"),
    y: z.number().optional().describe("Top edge of region to OCR"),
    width: z.number().optional().describe("Region width"),
    height: z.number().optional().describe("Region height"),
  },
  async ({ imagePath, x, y, width, height }) => {
    try {
      const result = await readText(imagePath, x, y, width, height);
      const wordList = result.words
        .map(
          (w) =>
            `  "${w.text}" (conf=${w.confidence}%, x=${w.bbox.x}, y=${w.bbox.y}, w=${w.bbox.w}, h=${w.bbox.h})`,
        )
        .join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Recognized text:\n${result.text}\n\nWords (${result.words.length}):\n${wordList}`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "sample_color",
  "Get the exact RGB color of a single pixel at (x, y). Use this to confirm border colors, icon strokes, or hover states without parsing a full palette.",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    x: z.number().describe("X coordinate"),
    y: z.number().describe("Y coordinate"),
  },
  async ({ imagePath, x, y }) => {
    try {
      const c = await sampleColor(imagePath, x, y);
      return { content: [{ type: "text", text: `(${x}, ${y}) → ${c.hex} (${c.rgb})` }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "analyze_font",
  "Heuristic font analysis on a cropped text region. Detects: serif vs sans-serif, weight (light/regular/bold/black), x-height ratio, stroke contrast. Suggests matching web fonts from Google Fonts. NOTE: this is a heuristic, not an identifier — for exact match, use crop_with_transparency to stamp the text directly.",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    x: z.number().describe("Left edge of text region"),
    y: z.number().describe("Top edge of text region"),
    width: z.number().describe("Region width"),
    height: z.number().describe("Region height"),
  },
  async ({ imagePath, x, y, width, height }) => {
    try {
      const result = await analyzeFont(imagePath, x, y, width, height);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "match_region",
  "Template matching: find where a region from one image appears in another. Returns the bounding box of the best match and a similarity score (0-100%). Useful for tracking an element across iterations — 'where did the hero text end up in my render?'",
  {
    imagePath: z.string().describe("Path to the larger image (where to search)"),
    templatePath: z.string().describe("Path to the image containing the template region"),
    x: z.number().describe("Left edge of the template region in templatePath"),
    y: z.number().describe("Top edge of the template region in templatePath"),
    width: z.number().describe("Template width"),
    height: z.number().describe("Template height"),
  },
  async ({ imagePath, templatePath, x, y, width, height }) => {
    try {
      const result = await matchRegion(imagePath, templatePath, x, y, width, height);
      return {
        content: [
          {
            type: "text",
            text: `Best match: x=${result.found.x}, y=${result.found.y}, w=${result.found.width}, h=${result.found.height}\nSimilarity: ${result.similarity}%`,
          },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "fit_to_view",
  "Render HTML at a size that fits in a target viewport (default 1440x900) while preserving the reference image's aspect ratio. Use this for PREVIEW (when you want to see the whole thing in one screen without zooming out). The native 2940x1548 render is for diffing only.",
  {
    html: z.string().describe("Full HTML document to render"),
    referencePath: z.string().describe("Reference image — used to determine aspect ratio"),
    maxWidth: z.number().default(1440).describe("Max viewport width (default 1440)"),
    maxHeight: z.number().default(900).describe("Max viewport height (default 900)"),
  },
  async ({ html, referencePath, maxWidth, maxHeight }) => {
    try {
      const result = await fitToView(html, referencePath, maxWidth, maxHeight);
      return { content: [{ type: "image", data: result.data, mimeType: result.mimeType }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "render_states",
  "Render the same HTML in multiple interaction states (default, hover on banner/CTA/nav/icon) and return a single composite image showing all states stacked vertically with labels. Use this to verify hover animations, focus rings, and other interactive CSS actually work.",
  {
    html: z.string().describe("Full HTML document"),
    width: z.number().default(1440).describe("Viewport width"),
    height: z.number().default(900).describe("Viewport height"),
  },
  async ({ html, width, height }) => {
    try {
      const result = await renderStates(html, width, height);
      return { content: [{ type: "image", data: result.data, mimeType: result.mimeType }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

server.tool(
  "classify_element",
  "Auto-classify a cropped region of an image so you know whether to render it with CSS+web font (text), inline SVG (simple icon), or as a transparent PNG stamp (complex pixel art, custom fonts). Returns kind, suggested approach, confidence, and the underlying metrics (color count, aspect ratio, color stddev).",
  {
    imagePath: z.string().describe("Absolute path to the image"),
    x: z.number().describe("Left edge of crop"),
    y: z.number().describe("Top edge of crop"),
    width: z.number().describe("Crop width"),
    height: z.number().describe("Crop height"),
  },
  async ({ imagePath, x, y, width, height }) => {
    try {
      const result = await classifyElement(imagePath, x, y, width, height);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  },
);

// ── Start ──
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("visual-diff-mcp running — HTML rendering + overlay comparison tools ready");
