// 59 — i18n (Internationalization)
// NEW CONCEPT: multi-language support.
// The client sends a language preference. The server returns messages in that language.
const express = require('express');
const app = express();
app.use(express.json());

// Translations
const translations = {
  en: { welcome: 'Welcome', error_not_found: 'Not found', error_unauthorized: 'You are not logged in', greeting: 'Hello, {name}!' },
  es: { welcome: 'Bienvenido', error_not_found: 'No encontrado', error_unauthorized: 'No has iniciado sesión', greeting: '¡Hola, {name}!' },
  fr: { welcome: 'Bienvenue', error_not_found: 'Non trouvé', error_unauthorized: 'Vous n\'êtes pas connecté', greeting: 'Bonjour, {name} !' },
};

const DEFAULT = 'en';
const SUPPORTED = Object.keys(translations);

function detectLocale(req) {
  // Query string
  if (req.query.lang && SUPPORTED.includes(req.query.lang)) return req.query.lang;
  // Accept-Language header
  const accept = req.headers['accept-language'] || '';
  for (const part of accept.split(',')) {
    const lang = part.split(';')[0].trim().split('-')[0];
    if (SUPPORTED.includes(lang)) return lang;
  }
  return DEFAULT;
}

function t(key, locale, vars = {}) {
  let str = translations[locale]?.[key] || translations[DEFAULT][key] || key;
  for (const [k, v] of Object.entries(vars)) str = str.replace(`{${k}}`, v);
  return str;
}

// Middleware
app.use((req, res, next) => {
  req.locale = detectLocale(req);
  req.t = (key, vars) => t(key, req.locale, vars);
  res.set('Content-Language', req.locale);
  next();
});

app.get('/', (req, res) => res.json({ message: req.t('welcome'), locale: req.locale, supported: SUPPORTED }));

app.get('/greet/:name', (req, res) => res.json({ message: req.t('greeting', { name: req.params.name }) }));

app.get('/error/404', (req, res) => res.status(404).json({ error: { code: 'not_found', message: req.t('error_not_found') } }));

app.get('/error/401', (req, res) => res.status(401).json({ error: { code: 'unauthorized', message: req.t('error_unauthorized') } }));

app.listen(3000, () => console.log('i18n on http://localhost:3000'));
