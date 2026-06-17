// i18n Demo — Multi-language messages, locale detection, translation lookup.
const express = require('express');
const app = express();
app.use(express.json());

// === Translations ===
const translations = {
  en: { welcome: 'Welcome', goodbye: 'Goodbye', error_not_found: 'Not found', error_unauthorized: 'You are not logged in', greeting: 'Hello, {name}!', cart_total: 'Cart total: ${total}' },
  es: { welcome: 'Bienvenido', goodbye: 'Adiós', error_not_found: 'No encontrado', error_unauthorized: 'No has iniciado sesión', greeting: '¡Hola, {name}!', cart_total: 'Total del carrito: ${total}' },
  fr: { welcome: 'Bienvenue', goodbye: 'Au revoir', error_not_found: 'Non trouvé', error_unauthorized: 'Vous n\'êtes pas connecté', greeting: 'Bonjour, {name} !', cart_total: 'Total du panier : ${total}' },
  de: { welcome: 'Willkommen', goodbye: 'Auf Wiedersehen', error_not_found: 'Nicht gefunden', error_unauthorized: 'Sie sind nicht angemeldet', greeting: 'Hallo, {name}!', cart_total: 'Warenkorb insgesamt: ${total}' },
  ja: { welcome: 'ようこそ', goodbye: 'さようなら', error_not_found: '見つかりません', error_unauthorized: 'ログインしていません', greeting: 'こんにちは、{name}さん！', cart_total: 'カートの合計：${total}' },
};

const defaultLocale = 'en';
const supported = Object.keys(translations);

function detectLocale(req) {
  // 1. Query string
  if (req.query.lang && supported.includes(req.query.lang)) return req.query.lang;
  // 2. Cookie
  if (req.cookies?.lang && supported.includes(req.cookies.lang)) return req.cookies.lang;
  // 3. Accept-Language header
  const accept = req.headers['accept-language'] || '';
  for (const part of accept.split(',')) {
    const lang = part.split(';')[0].trim().split('-')[0];
    if (supported.includes(lang)) return lang;
  }
  return defaultLocale;
}

function t(key, locale = defaultLocale, vars = {}) {
  let str = translations[locale]?.[key] || translations[defaultLocale][key] || key;
  for (const [k, v] of Object.entries(vars)) str = str.replace(`{${k}}`, v).replace(`\${${k}}`, v);
  return str;
}

// === Middleware: add t() and locale to request ===
app.use((req, res, next) => {
  req.locale = detectLocale(req);
  req.t = (key, vars) => t(key, req.locale, vars);
  res.set('Content-Language', req.locale);
  next();
});

// === Routes ===
app.get('/', (req, res) => res.json({ message: req.t('welcome'), locale: req.locale, supported }));

app.get('/me', (req, res) => {
  const name = req.query.name || 'friend';
  res.json({ greeting: req.t('greeting', { name }) });
});

app.get('/cart', (req, res) => {
  const total = parseFloat(req.query.total) || 99.99;
  res.json({ message: req.t('cart_total', { total: total.toFixed(2) }) });
});

app.get('/protected', (req, res) => {
  if (!req.headers.authorization) return res.status(401).json({ error: { code: 'unauthorized', message: req.t('error_unauthorized') } });
  res.json({ secret: 'data' });
});

app.get('/missing/:id', (req, res) => res.status(404).json({ error: { code: 'not_found', message: req.t('error_not_found') } }));

app.get('/admin/translations', (req, res) => res.json({ supported, defaultLocale, translations }));

app.listen(3000, () => console.log('i18n demo :3000 — pass ?lang=es or Accept-Language header'));
module.exports = app;
