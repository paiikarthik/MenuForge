"""Seed initial restaurant catalog dishes into local SQLite database."""

from __future__ import annotations

from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from menuforge.app import _db, _ensure_db
from menuforge.demo import generate_demo
from menuforge.models import GenerateRequest, Voice


def seed():
    _ensure_db()
    with _db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM menus").fetchone()[0]
        if count > 0:
            print(f"Catalog already contains {count} dishes.")
            return

        samples = [
            (
                "Coastal Leaf",
                "Mangalorean / Coastal Karnataka",
                "Kori Gassi",
                "Mains & Curries",
                "₹420 / $18.50",
                "Tulu",
                ["English", "Spanish", "Hindi"],
                Voice.family,
                "chicken, roasted coconut, Byadgi chili, curry leaves, tamarind",
                "Grandmother's Sunday feast curry from Mangalore.",
            ),
            (
                "Casa Puebla",
                "Mexican / Puebla",
                "Mole Poblano",
                "Chef's Specials",
                "$22.00",
                "Spanish",
                ["English", "Spanish", "French"],
                Voice.fine_dining,
                "dried chiles, Mexican cacao, sesame seeds, almonds, cloves",
                "Ceremonial festival mole ground in-house on Thursdays.",
            ),
            (
                "Saigon Corner",
                "Vietnamese Street Food",
                "Bánh Mì Đặc Biệt",
                "Street Bites & Sandwiches",
                "$11.50",
                "Vietnamese",
                ["English", "Spanish", "French"],
                Voice.street,
                "baguette, liver pâté, roasted pork char siu, pickled daikon-carrot, cilantro",
                "The quintessential Saigon street sandwich. Crisp crust, savory and bright.",
            ),
            (
                "Sichuan Pavilion",
                "Sichuan / Chengdu",
                "Mapo Tofu (麻婆豆腐)",
                "Mains & Curries",
                "$16.00",
                "Chinese",
                ["English", "Spanish", "French"],
                Voice.neighborhood,
                "silken tofu, aged Pixian doubanjiang, fermented douchi, chili oil, toasted Sichuan peppercorn",
                "Fiery, fragrant, and tingling with authentic numbing málà complexity.",
            ),
        ]

        for rest, cuis, dish, cat, price, src, tgts, v, ing, story in samples:
            req = GenerateRequest(
                restaurant_name=rest,
                cuisine=cuis,
                dish_name=dish,
                category=cat,
                price=price,
                source_language=src,
                target_languages=tgts,
                voice=v,
                ingredients=ing,
                story=story,
            )
            res = generate_demo(req, has_image=False)
            cur = conn.execute(
                "INSERT INTO menus (created_at, dish_name, category, price, payload) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    res.original_dish,
                    res.category,
                    res.price,
                    res.model_dump_json(),
                ),
            )
            row_id = cur.lastrowid
            res.id = row_id
            conn.execute(
                "UPDATE menus SET payload = ? WHERE id = ?",
                (res.model_dump_json(), row_id),
            )
        print("Seeded 4 initial authentic dishes into data/menuforge.db")


if __name__ == "__main__":
    seed()
