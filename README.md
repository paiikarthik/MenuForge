# MenuForge 🍳

> **Local-first AI menu studio for independent and heritage restaurants.**  
> Turn dish names, secret spice notes, and plating photos into bilingual menu cards, server pronunciation guides, and print-ready table tents with dynamic QR codes.  
> Powered by open-weight models via [Ollama](https://ollama.com). Confidential recipes and plating photos never leave `127.0.0.1`.

Built for the **[Hacktoberfest Open-Source AI Challenge: Week 3 — Side Hustle](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)**.

---

## 💡 The Real-World Problem

Neighborhood ethnic restaurants operate on razor-thin margins (3%–9%). When an independent restaurant owner (from Mangalorean seafood spots to Oaxacan taquerias, Vietnamese bánh mì stalls, or Sichuan dumpling houses) wants to translate their menu or print seasonal specials:

1. **Closed SaaS & Translators flatten heritage:** Generic translation tools translate *Kori Gassi* to "chicken curry", *Mole Poblano* to "chocolate sauce stew", and *Mapo Tofu* to "bean curd in chili". It erases culinary identity, authenticity, and artisan pricing power.
2. **Server turnover causes chaos:** Waitstaff struggle to pronounce cultural names, fumble when customers ask what ingredients are in the dish, and fail to upsell pairings.
3. **Allergen liabilities:** Hand-written specials boards frequently miss hidden allergens (ghee, sesame, crustacean paste, tree nuts).
4. **Cloud API token economics kill the business:** Paying $0.05–$0.15 per API call plus cloud subscription fees makes a low-cost $49 setup or $15/month side-hustle unprofitable.

---

## 🚀 Why Open-Weight Models Win Here

| Feature | Closed Cloud APIs (OpenAI / Claude) | MenuForge + Ollama (Open Weights) |
|---|---|---|
| **Marginal Cost Per Dish** | Metered token fees ($0.03–$0.12/call) | **$0.00** after initial model pull |
| **Recipe Confidentiality** | Secret family recipes sent to third-party cloud | **100% on-premise** on `127.0.0.1` |
| **Kitchen Network Resilience** | Fails during spotty basement kitchen WiFi drops | **100% offline ready**; runs without internet |
| **Cultural Name Retention** | Dumbs down proper nouns to generic descriptors | Preserves authentic names with phonetic guides |
| **Custom Domain Fine-Tuning** | Vendor lock-in; prompt-engineering workarounds | Adaptable & fine-tunable on local culinary corpora |

---

## 🛠️ Features

- 🍛 **Authentic Cultural Preservation:** Protects native proper nouns while generating nuanced English, Spanish, Hindi, French, German, or Chinese descriptions.
- 🔊 **Server Pronunciation & Web Audio:** Generates intuitive phonetic breakdowns (e.g. `KO-ri GAH-see`) with a live 🔊 **"Listen"** audio speech synthesis button for waitstaff training.
- ⚠️ **Automated Allergen & Dietary Matrix:** Detects allergens (dairy, nuts, shellfish, wheat, soy, sesame) and tags dietary suitability (Vegan, Gluten-Free, Halal-friendly).
- 🖨️ **Print Studio:**
  - **Foldable Table Tent Cards (4" x 6"):** Two-sided table talkers with front heritage blurb and back translation, pairings, and an embedded SVG QR code.
  - **Waitstaff Shift Pocket Cards (3" x 5"):** Quick-reference cheat sheet for pre-shift lineup (phonetics, 15-second table pitch, allergen warnings, drink upsells).
  - **Full Restaurant Menu Print Layout:** Multi-section print-ready restaurant menu with clean typography.
- 📖 **Local SQLite Menu Catalog:** Saves all dishes into `data/menuforge.db` with course categorization, pricing, and 1-click JSON/Markdown export for POS systems (Square, Toast, Clover).
- ⚡ **Zero-Download Demo Engine:** Pre-loaded with 6 rich culinary fixtures (Mangalore, Puebla, Saigon, Chengdu, Addis Ababa, Taipei) and intelligent heuristics, so judges and offline users can test everything immediately.

---

## 🏁 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/paiikarthik/MenuForge.git
cd MenuForge
pip install -r requirements.txt
```

### 2. Generate Sample Art & Seed Demo Data

```bash
python scripts/make_samples.py
python scripts/seed_demo.py
```

### 3. Launch MenuForge

```bash
python -m menuforge
```

Open **[http://127.0.0.1:8765](http://127.0.0.1:8765)** in your browser.

---

## 🤖 Using Local Open Weights (Optional)

Install [Ollama](https://ollama.com) and pull your preferred open weights:

```bash
# Lightweight fast text model (recommended):
ollama pull llama3.2:3b

# Or Qwen 2.5:
ollama pull qwen2.5:3b

# Optional vision model for photo-aware plating analysis:
ollama pull llava:7b
```

MenuForge auto-detects installed models via `/api/health` and lists them in the model picker dropdown. If Ollama is offline, MenuForge automatically falls back to its embedded offline culinary engine.

---

## 🧪 Running the Test Suite

```bash
pytest tests -v
```

All 7 test suites verify:
- Health check & local model discovery
- Sample endpoint serving all 6 culinary fixtures
- Generation pipeline & heuristic allergen extraction
- SQLite CRUD lifecycle, category filtering & JSON/Markdown export
- Static asset serving & image badge delivery

---

## 💼 Business Model: The $49 Side Hustle

- **$49 Onboarding Setup:** Digitize 20–25 signature dishes for an independent neighborhood eatery. Deliver branded bilingual menu cards, waitstaff pocket flashcards, and laminated QR table tent stands.
- **$15/month Seasonal Retainer:** Weekly specials updates, blackboard chalk copy, and seasonal menu rotation.
- **Economics:** Because inference runs on open weights on a cheap laptop or mini-PC, marginal cost is **$0**. A solo operator servicing 20 restaurants generates **$300/mo recurring + setup fees** with near 100% gross margins.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
