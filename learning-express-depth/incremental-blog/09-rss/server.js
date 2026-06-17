// 09-rss: Generate RSS and Atom feeds. Let readers subscribe to your blog.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const SITE_URL = process.env.SITE_URL || 'http://localhost:3000';
const SITE_TITLE = 'My Blog';
const SITE_DESCRIPTION = 'A blog about backend development';
const AUTHOR_EMAIL = 'admin@example.com';

const db = new Database(':memory:');
db.exec(`CREATE TABLE posts (id INTEGER PRIMARY KEY, slug TEXT, title TEXT, body TEXT, excerpt TEXT, status TEXT, published_at TEXT, author_email TEXT)`);

function escapeXml(s) {
  return s.replace(/[<>&'"]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[c]));
}

// RSS 2.0 feed
app.get('/feed.xml', (req, res) => {
  const posts = db.prepare("SELECT * FROM posts WHERE status = 'published' ORDER BY published_at DESC LIMIT 20").all();
  const items = posts.map(p => `
    <item>
      <title>${escapeXml(p.title)}</title>
      <link>${SITE_URL}/posts/${p.slug}</link>
      <guid>${SITE_URL}/posts/${p.slug}</guid>
      <pubDate>${new Date(p.published_at).toUTCString()}</pubDate>
      <description>${escapeXml(p.excerpt || p.body.slice(0, 200))}</description>
    </item>
  `).join('');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(SITE_TITLE)}</title>
    <link>${SITE_URL}</link>
    <description>${escapeXml(SITE_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${items}
  </channel>
</rss>`;
  res.set('Content-Type', 'application/rss+xml');
  res.send(xml);
});

// Atom feed (alternative format)
app.get('/atom.xml', (req, res) => {
  const posts = db.prepare("SELECT * FROM posts WHERE status = 'published' ORDER BY published_at DESC LIMIT 20").all();
  const entries = posts.map(p => `
    <entry>
      <title>${escapeXml(p.title)}</title>
      <link href="${SITE_URL}/posts/${p.slug}"/>
      <id>${SITE_URL}/posts/${p.slug}</id>
      <updated>${new Date(p.published_at).toISOString()}</updated>
      <summary>${escapeXml(p.excerpt || p.body.slice(0, 200))}</summary>
    </entry>
  `).join('');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${escapeXml(SITE_TITLE)}</title>
  <link href="${SITE_URL}"/>
  <updated>${new Date().toISOString()}</updated>
  <id>${SITE_URL}/</id>
  ${entries}
</feed>`;
  res.set('Content-Type', 'application/atom+xml');
  res.send(xml);
});

// JSON Feed (modern alternative)
app.get('/feed.json', (req, res) => {
  const posts = db.prepare("SELECT * FROM posts WHERE status = 'published' ORDER BY published_at DESC LIMIT 20").all();
  res.json({
    version: 'https://jsonfeed.org/version/1.1',
    title: SITE_TITLE,
    home_page_url: SITE_URL,
    feed_url: `${SITE_URL}/feed.json`,
    items: posts.map(p => ({
      id: `${SITE_URL}/posts/${p.slug}`,
      url: `${SITE_URL}/posts/${p.slug}`,
      title: p.title,
      summary: p.excerpt,
      content_text: p.body,
      date_published: new Date(p.published_at).toISOString(),
    })),
  });
});

app.listen(3000, () => console.log('09-rss on :3000 (try /feed.xml, /atom.xml, /feed.json)'));
