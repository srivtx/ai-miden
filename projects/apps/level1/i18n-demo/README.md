# i18n Demo — Multi-language messages, locale detection, variable substitution

Serve error messages and UI strings in the user's language. Detect locale from query, cookie, or `Accept-Language` header.

## Endpoints
```
GET /                       # welcome in current locale
GET /me?name=Alice          # personalized greeting
GET /cart?total=99.99       # formatted cart total
GET /protected              # 401 in current locale
GET /missing/123            # 404 in current locale
GET /admin/translations     # all translations
```

## Try
```bash
# English
curl http://localhost:3000/

# Spanish
curl 'http://localhost:3000/?lang=es'

# French (from Accept-Language)
curl -H 'Accept-Language: fr-FR,fr;q=0.9' http://localhost:3000/

# Japanese
curl 'http://localhost:3000/?lang=ja'

# Personalized
curl 'http://localhost:3000/me?lang=es&name=Alice'
# { greeting: "¡Hola, Alice!" }
```

## What this teaches
1. **Translation files**: nested keys per language
2. **Locale detection**: query > cookie > Accept-Language > default
3. **Variable substitution**: `{name}`, `${total}` placeholders
4. **Fallback**: missing key → default language
5. **`Content-Language` header**: tell the client which language you used
6. **Right-to-left and CJK**: same pattern, different strings
