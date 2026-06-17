# 59 — i18n (Internationalization)

**New concept:** multi-language support. The client picks a language. The server returns messages in that language.

## Run it

```bash
npm install
node server.js
```

```bash
# English (default)
curl http://localhost:3000/
# { "message": "Welcome", "locale": "en", "supported": ["en", "es", "fr"] }

# Spanish
curl 'http://localhost:3000/?lang=es'
# { "message": "Bienvenido", "locale": "es", ... }

# French via Accept-Language header
curl -H "Accept-Language: fr-FR,fr;q=0.9" http://localhost:3000/
# { "message": "Bienvenue", "locale": "fr", ... }

# Personalized greeting
curl 'http://localhost:3000/greet/Alice?lang=es'
# { "message": "¡Hola, Alice!" }

# Error messages in different languages
curl 'http://localhost:3000/error/404?lang=fr'
# { "error": { "code": "not_found", "message": "Non trouvé" } }
```

## How to think about it

When you build an app for the world, not everyone speaks your language. i18n lets each user pick. The server has a translation table for each supported language. The client tells the server which one to use.

## How to build it (line by line)

```js
const translations = {
  en: { welcome: 'Welcome' },
  es: { welcome: 'Bienvenido' },
  fr: { welcome: 'Bienvenue' },
};
```

**Lines 8-12.** A nested object: language → key → translation.

```js
function detectLocale(req) {
  if (req.query.lang && SUPPORTED.includes(req.query.lang)) return req.query.lang;
  // ... Accept-Language header parsing ...
  return DEFAULT;
}
```

**Lines 20-26.** Detect which language the client wants. Three ways:
1. Query string: `?lang=es`
2. Accept-Language header (what browsers send)
3. Default (English)

```js
function t(key, locale, vars = {}) {
  let str = translations[locale]?.[key] || translations[DEFAULT][key] || key;
  for (const [k, v] of Object.entries(vars)) str = str.replace(`{${k}}`, v);
  return str;
}
```

**Lines 28-32.** Get a translation, with variable substitution.

**`translations[locale]?.[key]`** — the `?.` means "if locale is not in the table, use the default."

**`str.replace('{name}', value)`** — replace `{name}` with the actual value. This is how you do "Hello, {name}!"

## What we learned

1. i18n = internationalization
2. Translation tables: language → key → string
3. Locale detection: query string, Accept-Language header, default
4. Variable substitution: `{name}` becomes the actual name
5. The `Content-Language` header tells the client which language was used
6. Real systems: i18next, FormatJS, gettext

## What's next

In **60-validation-joi** we use Joi, a powerful validation library, instead of writing our own.
