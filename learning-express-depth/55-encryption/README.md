# 55 — Encryption

**New concept:** encrypting data at rest.

We hashed passwords in project 14 (one-way: you can't un-hash). Encryption is two-way: encrypt to hide, decrypt to read.

Useful for: notes, messages, API keys, anything sensitive you need to read later.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a note (encrypted at rest)
curl -X POST http://localhost:3000/notes \
  -H "Content-Type: application/json" \
  -d '{"text": "My secret thought"}'
# 201 { "id": 1 }

# Get the note (decrypted on the way out)
curl http://localhost:3000/notes/1
# { "id": 1, "text": "My secret thought", "createdAt": "..." }

# Admin: see the raw encrypted form
curl http://localhost:3000/admin/notes
# { "notes": [{ "id": 1, "encrypted": "a3b4c5...:deadbeef..." }] }
# Even if someone steals the database, they can't read the notes
```

## How to think about it

Hashing is for passwords — you never need to read the original. Encryption is for data you need to read back — like notes, messages, files.

## How to build it (line by line)

```js
const KEY = Buffer.from('12345678901234567890123456789012');  // 32 bytes
```

**Line 8.** The encryption key. 32 bytes for AES-256.

**`Buffer.from(string)`** — convert a string to bytes. In production, generate a random key and store it in a secret manager.

```js
function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', KEY, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}
```

**Lines 11-17.** Encrypt text.

**`iv`** — initialization vector. Random bytes that make each encryption unique. Without it, encrypting the same text twice gives the same result (bad).

**`aes-256-cbc`** — the algorithm. AES, 256-bit key, CBC mode.

**`cipher.update(...)`** — feed in the data.

**`cipher.final(...)`** — get the last chunk (handles padding).

```js
const text = decrypt(note.encrypted);
```

**Line 40.** Decrypt when we need to read it back. The same key, the same IV, and the result is the original text.

## What we learned

1. Encryption is two-way, hashing is one-way
2. AES-256 is a common algorithm
3. IV (initialization vector) makes each encryption unique
4. The key is the secret — protect it
5. Real systems use libraries like bcrypt (for hashing) and crypto (for encryption)

## What's next

In **56-csrf** we protect against Cross-Site Request Forgery.
