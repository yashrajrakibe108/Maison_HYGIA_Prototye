# Maison Hygia - AI Ritual Concierge (Simple Version)

A beginner-friendly prototype. **No AI libraries, no API keys, no installs needed** -
just plain Python, so every line is easy to read and explain out loud.

## Run it

```bash
python concierge_simple.py
```

That's it. No `pip install` required.

## The big idea, in plain language

A customer types a message like:

> "My skin feels dry lately, I'm not sleeping well, and I want a simple evening routine."

The concierge does 4 things, in order:

| Step | What it does | Plain-language explanation |
|---|---|---|
| **1. Understand** | Reads the message and pulls out key facts (concerns, time of day, "keep it simple?") | Looks for keywords like "dry", "sleep", "simple" |
| **2. Retrieve** | Compares the message to every product's description | Counts how many words the message and each product description have in common - more shared words = more relevant. (This is a simple stand-in for what real AI systems call "RAG" - Retrieval-Augmented Generation - which uses AI embeddings instead of word-counting) |
| **3. Recommend** | Picks the best 2–3 products, fairly | Scores mostly by relevance (85%) and only a little by how profitable the product is (15%) - so profit can only break ties, never override relevance |
| **4. Explain** | Tells the customer why each product was picked | Names the actual concern + ingredient + benefit, and never makes a medical claim |

## The most important part: fairness

The prototype also shows what would happen if we *did* let profit drive
recommendations - and it's a genuinely bad outcome. In the code, this is
the difference between two scoring formulas:

```python
# What we actually ship - relevance matters most
score = (relevance * 0.85) + (margin * 0.15)

# What we DON'T ship - profit matters most (the mistake to avoid)
score = (relevance * 0.2) + (margin * 0.8)
```

Run the script and compare the "Recommended routine" section against the
"COMPARISON" section - you'll see the profit-first version sometimes swaps
in a less relevant, more expensive product. That's the exact problem the
case study asks candidates to design against.

## Files

- `products.json` - 8 made-up Maison Hygia products with prices, ingredients, and which customer concerns they help with
- `concierge_simple.py` - the whole prototype, step by step, in plain Python
- `README.md` - this file

## Honest limitations (say this out loud in your presentation - it shows self-awareness)

- Word-counting isn't true language understanding - it can miss a
  relevant product if it uses different words than the customer, or
  match on a shared word that isn't actually meaningful (e.g. both
  mentioning "skin"). A real version would use an AI embedding model
  so it understands meaning, not just shared words.
- The "understand the message" step uses a fixed keyword list. A real
  version would use an LLM (like Claude) so it generalizes to messages
  we didn't anticipate.
- There's no memory between conversations yet - a real version would
  remember the customer's preferences for next time.
- No automatic check yet for accidental medical claims in the
  explanation text - right now this is handled by keeping the template simple.
