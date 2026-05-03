# What is Token-Level Attack

---

## 1. Why it exists (THE PROBLEM)

Most safety defenses operate at the **word or sentence level**: keyword blocklists, semantic classifiers, and perplexity filters. These defenses assume that harmful content looks harmful to a human reader.

But what if the prompt **looks harmless to humans** while being interpreted as harmful by the model? Attackers discovered that tiny, invisible, or visually similar character manipulations can bypass filters entirely.

**Token-level attacks exist because model tokenizers and human perception are not the same.** A prompt that passes visual inspection can still trigger malicious behavior in the model's token embedding space.

---

## 2. Definition (very simple)

**Token-level attacks** are adversarial techniques that manipulate individual characters, bytes, or tokens in a prompt to evade detection while preserving semantic meaning or achieving a malicious goal.

Common forms include:
- **Character-level perturbations:** Replacing letters with similar-looking ones (`a` → `а` Cyrillic)
- **Homoglyphs:** Using visually identical characters from different Unicode blocks
- **Invisible characters:** Inserting zero-width spaces, joiners, or control characters
- **Token smuggling:** Splitting a banned word across multiple tokens in unusual ways

---

## 3. Real-life analogy

Imagine sending a **secret message** through airport security.

- You write "bomb" on a piece of paper. Security sees it and confiscates it. (Blocked by keyword filter.)
- You write "bоmb" using a Cyrillic 'о' that looks identical to a Latin 'o'. A human guard glances at it and sees "bomb," but the OCR scanner sees a different Unicode string and doesn't flag it. (Homoglyph attack.)
- You write "b\u200bom\u200bb" with invisible zero-width spaces between each letter. To a human, it looks like "bomb." To a simple regex filter `/bomb/`, it does not match. (Invisible character attack.)
- Token-level attacks are steganography for AI prompts.

---

## 4. Tiny numeric example

Consider the word "hack" and three tokenization schemes.

```
Standard tokenization:
  "hack" → [token_id: 1042]
  Filter sees [1042] and blocks it.

Homoglyph substitution (Cyrillic 'а'):
  "hаck" → [token_id: 104, 97, 99, 107]  (4 separate tokens)
  Filter looking for [1042] does not block it.
  Model embedding sees similar vectors → interprets as "hack"

Invisible character insertion:
  "h\u200back" → [token_id: 104, 8203, 97, 99, 107]
  Regex /hack/ fails.
  Tokenizer still produces interpretable embeddings.
```

**Numeric impact:**
- Baseline harmfulness score: 0.95 (blocked)
- Homoglyph prompt harmfulness: 0.91 (bypasses regex, model still complies)
- Invisible char prompt harmfulness: 0.88 (bypasses visual inspection, model still complies)

---

## 5. Common confusion

- **Token-level attacks are not the same as typos.** A typo (`hte` instead of `the`) is unintentional. Token-level attacks are carefully chosen substitutions designed to evade specific filters while remaining semantically effective.
- **Token-level attacks do not always fool the model.** Some tokenizers normalize Unicode (NFC/NFD) before encoding, stripping homoglyphs or invisible characters. Attacks must target the specific tokenizer in use.
- **Token-level attacks are not only about bypassing AI.** They also bypass human moderators, keyword lists, and legacy regex-based content filters that predate LLMs.
- **Invisible characters are not truly invisible to all systems.** A robust defense can sanitize input by removing control characters and normalizing Unicode before tokenization.
- **Homoglyphs are not limited to Cyrillic.** Greek, Armenian, and mathematical symbols also contain visually identical characters (e.g., Greek `ο` vs Latin `o`).
- **Token smuggling is not encryption.** It does not hide meaning from a determined analyst. It only exploits the gap between a specific filter's logic and the tokenizer's behavior.
- **Character-level attacks are not obsolete.** Even state-of-the-art models can be vulnerable to carefully crafted token sequences that fall into rare embedding regions.

---

## 6. Where it is used in our code

In `src/phase68/phase68_jailbreak_advanced_colab.py`, we demonstrate token-level evasion in the defense module:

```python
# Defense: Input sanitization against token-level attacks
def sanitize_input(text):
    # Normalize Unicode to strip homoglyphs
    text = unicodedata.normalize('NFKC', text)
    
    # Remove invisible characters
    text = re.sub(r'[\u200b-\u200f\ufeff\u2060]', '', text)
    
    # Strip excessive whitespace/control chars
    text = re.sub(r'[\x00-\x1f]', '', text)
    
    return text

# Example:
# "hаck" (Cyrillic 'а') → "hack" after NFKC normalization
```

This shows how token-level attacks are countered at the preprocessing stage.
