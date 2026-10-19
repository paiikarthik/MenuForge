from __future__ import annotations

import io
import json
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from .demo import generate_demo
from .models import GenerateRequest, MenuResult, Voice
from .ollama_client import OllamaClient, encode_image

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
DATA = ROOT / "data"
DB_PATH = DATA / "menuforge.db"
MAX_IMAGE_BYTES = 8 * 1024 * 1024

@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_db() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                dish_name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Main Course',
                price TEXT NOT NULL DEFAULT '',
                payload TEXT NOT NULL
            )
            """
        )
        cur = conn.execute("PRAGMA table_info(menus)")
        cols = [row[1] for row in cur.fetchall()]
        if "category" not in cols:
            conn.execute("ALTER TABLE menus ADD COLUMN category TEXT NOT NULL DEFAULT 'Main Course'")
        if "price" not in cols:
            conn.execute("ALTER TABLE menus ADD COLUMN price TEXT NOT NULL DEFAULT ''")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_db()
    yield


app = FastAPI(
    title="MenuForge",
    description="Local AI menu translator & menu studio for independent restaurants",
    version="0.2.0",
    lifespan=lifespan,
)


def _ollama() -> OllamaClient:
    return OllamaClient(base_url=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))


@app.get("/api/health")
async def health():
    client = _ollama()
    online = await client.available()
    models: list[str] = []
    if online:
        try:
            models = await client.list_models()
        except Exception:
            models = []
    return {
        "ok": True,
        "ollama": online,
        "models": models,
        "demo_fallback": True,
        "message": (
            f"Ollama connected ({len(models)} local models detected) — $0 marginal cost per dish."
            if online
            else "Ollama offline — running embedded zero-download demo engine with authentic cultural fixtures."
        ),
    }


@app.get("/api/samples")
async def samples():
    return {
        "samples": [
            {
                "id": "kori-gassi",
                "restaurant_name": "Coastal Leaf",
                "cuisine": "Mangalorean / Coastal Karnataka",
                "dish_name": "Kori Gassi",
                "category": "Mains & Curries",
                "price": "₹420 / $18.50",
                "source_language": "Tulu / Kannada",
                "target_languages": ["English", "Spanish", "Hindi"],
                "ingredients": "country chicken, freshly grated roasted coconut, Byadgi red chilies, curry leaves, tamarind pulp, coriander seeds",
                "story": "Owner grandmother Sunday feast curry from Mangalore. Medium-hot by default; coconut balances the deep red chili warmth.",
                "allergens_known": "dairy (if finished with ghee), coconut",
                "voice": "family",
                "image": "/samples/kori-gassi.jpg",
            },
            {
                "id": "mole-poblano",
                "restaurant_name": "Casa Puebla",
                "cuisine": "Mexican / Puebla",
                "dish_name": "Mole Poblano",
                "category": "Chef's Specials",
                "price": "$22.00",
                "source_language": "Spanish",
                "target_languages": ["English", "Spanish", "French"],
                "ingredients": "ancho, pasilla & mulato chiles, Mexican stone-ground cacao, sesame seeds, almonds, cloves, cinnamon, slow-simmered poultry",
                "story": "Ceremonial festival mole ground in-house on Thursdays. Rich, complex, savoury-smoky, never cloying.",
                "allergens_known": "sesame, tree nuts (almonds), gluten",
                "voice": "fine_dining",
                "image": "/samples/mole-poblano.jpg",
            },
            {
                "id": "banh-mi",
                "restaurant_name": "Saigon Corner",
                "cuisine": "Vietnamese Street Food",
                "dish_name": "Bánh Mì Đặc Biệt",
                "category": "Street Bites & Sandwiches",
                "price": "$11.50",
                "source_language": "Vietnamese",
                "target_languages": ["English", "Spanish", "French"],
                "ingredients": "crisp airy baguette, house liver pâté, roasted pork char siu, cucumber ribbons, fresh cilantro, pickled daikon-carrot",
                "story": "The quintessential Saigon street sandwich. Baked fresh at 6 AM; crunchy crust with savory-sweet tang.",
                "allergens_known": "wheat/gluten, soy, egg (house mayo)",
                "voice": "street",
                "image": "/samples/banh-mi.jpg",
            },
            {
                "id": "mapo-tofu",
                "restaurant_name": "Sichuan Pavilion",
                "cuisine": "Sichuan / Chengdu",
                "dish_name": "Mapo Tofu (麻婆豆腐)",
                "category": "Mains & Curries",
                "price": "$16.00",
                "source_language": "Chinese (Simplified)",
                "target_languages": ["English", "Spanish", "French"],
                "ingredients": "silken tofu, aged Pixian doubanjiang chili-bean paste, fermented douchi black beans, chili oil, ground toasted Sichuan flower peppercorns",
                "story": "Chengdu signature wok creation. Fiery, fragrant, and tingling with authentic numbing 'málà' complexity.",
                "allergens_known": "soy, sesame",
                "voice": "neighborhood",
                "image": "/samples/mapo-tofu.jpg",
            },
            {
                "id": "doro-wat",
                "restaurant_name": "Lalibela Kitchen",
                "cuisine": "Ethiopian / Addis Ababa",
                "dish_name": "Doro Wat",
                "category": "Mains & Curries",
                "price": "$21.00",
                "source_language": "Amharic",
                "target_languages": ["English", "Spanish", "French"],
                "ingredients": "chicken slow-braised in red onions, sun-dried berbere chili blend, ginger, garlic, niter kibbeh spiced butter, spice-infused hard-cooked egg",
                "story": "The centerpiece of Ethiopian communal hospitality, slow-simmered for 4 hours and served on sour teff injera.",
                "allergens_known": "dairy (spiced butter), egg",
                "voice": "family",
                "image": "/samples/doro-wat.jpg",
            },
            {
                "id": "gua-bao",
                "restaurant_name": "Taipei Night Market Bites",
                "cuisine": "Taiwanese Street Food",
                "dish_name": "Gua Bao (割包)",
                "category": "Street Bites & Sandwiches",
                "price": "$12.00",
                "source_language": "Traditional Chinese",
                "target_languages": ["English", "Spanish", "French"],
                "ingredients": "steamed lotus leaf bun, thick red-braised five-spice pork belly, fermented sour mustard greens, crushed sweetened peanut powder, fresh cilantro",
                "story": "Known fondly as the Taiwanese street burger — cloud-soft steamed bun hugging melting savory-sweet braised pork.",
                "allergens_known": "peanuts, wheat/gluten, soy",
                "voice": "street",
                "image": "/samples/gua-bao.jpg",
            },
        ]
    }


async def _read_image(upload: Optional[UploadFile]) -> Optional[bytes]:
    if upload is None or not upload.filename:
        return None
    data = await upload.read()
    if not data:
        return None
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(400, "Image must be under 8MB")
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.thumbnail((1280, 1280))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        return buf.getvalue()
    except Exception as exc:
        raise HTTPException(400, f"Could not read image: {exc}") from exc


@app.post("/api/generate", response_model=MenuResult)
async def generate(
    restaurant_name: str = Form(""),
    cuisine: str = Form(""),
    dish_name: str = Form(...),
    category: str = Form("Main Course"),
    price: str = Form(""),
    source_language: str = Form("auto"),
    target_languages: str = Form("English,Spanish"),
    ingredients: str = Form(""),
    story: str = Form(""),
    allergens_known: str = Form(""),
    voice: str = Form("neighborhood"),
    model: str = Form(""),
    force_demo: str = Form("false"),
    image: Optional[UploadFile] = File(None),
):
    langs = [x.strip() for x in target_languages.split(",") if x.strip()]
    if not langs:
        langs = ["English"]
    try:
        req = GenerateRequest(
            restaurant_name=restaurant_name,
            cuisine=cuisine,
            dish_name=dish_name,
            category=category or "Main Course",
            price=price or "",
            source_language=source_language,
            target_languages=langs,
            ingredients=ingredients,
            story=story,
            allergens_known=allergens_known,
            voice=Voice(voice),
            model=model or None,
            force_demo=force_demo.lower() in {"1", "true", "yes"},
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    image_bytes = await _read_image(image)
    has_image = bool(image_bytes)
    client = _ollama()
    use_demo = req.force_demo or not await client.available()

    if use_demo:
        result = generate_demo(req, has_image=has_image)
    else:
        try:
            b64 = encode_image(image_bytes) if image_bytes else None
            result = await client.generate_menu(req, image_b64=b64)
        except Exception as exc:
            result = generate_demo(req, has_image=has_image)
            result.qr_one_liner = (
                f"{result.qr_one_liner} (Demo fallback after local model note: {exc})"
            ).strip()

    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO menus (created_at, dish_name, category, price, payload) VALUES (?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                result.original_dish,
                result.category,
                result.price,
                result.model_dump_json(),
            ),
        )
        row_id = cur.lastrowid
        result.id = row_id
        # Update row with result that contains the id
        conn.execute(
            "UPDATE menus SET payload = ? WHERE id = ?",
            (result.model_dump_json(), row_id),
        )

    return result


@app.get("/api/history")
async def history(category: Optional[str] = None, limit: int = 50):
    limit = max(1, min(limit, 200))
    with _db() as conn:
        if category and category.lower() != "all":
            rows = conn.execute(
                "SELECT id, created_at, dish_name, category, price, payload FROM menus WHERE category = ? ORDER BY id DESC LIMIT ?",
                (category, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, created_at, dish_name, category, price, payload FROM menus ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()

    items = []
    for r in rows:
        try:
            parsed = json.loads(r[5])
            parsed["id"] = r[0]
        except Exception:
            parsed = {}
        items.append({
            "id": r[0],
            "created_at": r[1],
            "dish_name": r[2],
            "category": r[3],
            "price": r[4],
            "menu": parsed,
        })
    return {"items": items}


@app.delete("/api/history/{item_id}")
async def delete_item(item_id: int):
    with _db() as conn:
        conn.execute("DELETE FROM menus WHERE id = ?", (item_id,))
    return {"ok": True, "deleted": item_id}


@app.delete("/api/history")
async def clear_history():
    with _db() as conn:
        conn.execute("DELETE FROM menus")
    return {"ok": True, "cleared": True}


@app.get("/api/export")
async def export_catalog(format: str = "json"):
    with _db() as conn:
        rows = conn.execute("SELECT id, created_at, dish_name, category, price, payload FROM menus ORDER BY category, dish_name").fetchall()

    parsed_menus = []
    for r in rows:
        try:
            item = json.loads(r[5])
            item["id"] = r[0]
            parsed_menus.append(item)
        except Exception:
            continue

    if format.lower() == "markdown":
        md_lines = ["# Restaurant Menu Catalog\n", f"_Exported {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n\n"]
        current_cat = None
        for m in parsed_menus:
            cat = m.get("category", "Main Course")
            if cat != current_cat:
                current_cat = cat
                md_lines.append(f"## {current_cat}\n\n")
            md_lines.append(f"### {m.get('original_dish')} — {m.get('price', '')}\n")
            md_lines.append(f"**Cuisine:** {m.get('cuisine', '')} | **Spice:** {m.get('spice_level', '')} | **Pronunciation:** `{m.get('staff_pronunciation', '')}`\n\n")
            md_lines.append(f"> {m.get('qr_one_liner', '')}\n\n")
            if m.get("allergens"):
                md_lines.append(f"**Allergens:** {', '.join(m.get('allergens', []))}\n\n")
            if m.get("pairings"):
                md_lines.append(f"**Pairings:** {', '.join(m.get('pairings', []))}\n\n")
            for c in m.get("cards", []):
                md_lines.append(f"- **{c.get('language')}:** {c.get('short_blurb')}\n")
                md_lines.append(f"  _{c.get('full_description')}_\n")
            md_lines.append("\n---\n\n")
        return Response(content="".join(md_lines), media_type="text/markdown")

    return {"restaurant_menu": parsed_menus, "count": len(parsed_menus)}


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


app.mount("/samples", StaticFiles(directory=STATIC / "samples"), name="samples")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def main() -> None:
    import uvicorn

    uvicorn.run(
        "menuforge.app:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8765")),
        reload=False,
    )


if __name__ == "__main__":
    main()
