"""Comprehensive test suite for MenuForge."""

import io
import json
import sqlite3
import pytest
from fastapi.testclient import TestClient

from menuforge.app import app, DB_PATH, _ensure_db
from menuforge.models import GenerateRequest, Voice
from menuforge.demo import generate_demo, _infer_allergens, _infer_dietary, _infer_spice, _infer_pronunciation


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Point DB_PATH to a temporary sqlite database for tests."""
    test_db = tmp_path / "test_menuforge.db"
    monkeypatch.setattr("menuforge.app.DB_PATH", test_db)
    _ensure_db()
    yield


client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "ollama" in data
    assert "models" in data
    assert data["demo_fallback"] is True
    assert "message" in data


def test_samples_endpoint():
    res = client.get("/api/samples")
    assert res.status_code == 200
    data = res.json()
    assert "samples" in data
    assert len(data["samples"]) == 6

    sample_ids = [s["id"] for s in data["samples"]]
    assert "kori-gassi" in sample_ids
    assert "mole-poblano" in sample_ids
    assert "banh-mi" in sample_ids
    assert "mapo-tofu" in sample_ids
    assert "doro-wat" in sample_ids
    assert "gua-bao" in sample_ids


def test_generate_demo_fixture():
    req = GenerateRequest(
        restaurant_name="Coastal Leaf",
        cuisine="Mangalorean",
        dish_name="Kori Gassi",
        category="Mains & Curries",
        price="₹420",
        source_language="Tulu",
        target_languages=["English", "Spanish", "Hindi"],
        ingredients="chicken, roasted coconut, Byadgi chili",
        story="Grandmother's Sunday feast",
        voice=Voice.family,
    )
    result = generate_demo(req, has_image=False)
    assert result.original_dish == "Kori Gassi"
    assert result.category == "Mains & Curries"
    assert result.price == "₹420"
    assert result.spice_level == "hot"
    assert "KO-ri GAH-see" in result.staff_pronunciation
    assert len(result.cards) == 3
    card_langs = [c.language for c in result.cards]
    assert "English" in card_langs
    assert "Spanish" in card_langs
    assert "Hindi" in card_langs


def test_generate_custom_dish_heuristics():
    req = GenerateRequest(
        restaurant_name="Bao Craft",
        cuisine="Taiwanese",
        dish_name="Crispy Peanut Tofu Bao",
        category="Street Bites",
        price="$12.00",
        source_language="Mandarin",
        target_languages=["English", "Spanish"],
        ingredients="steamed wheat flour bun, crispy silken tofu, ground roasted peanuts, cilantro, chili oil",
        story="Night market stall favorite with a spicy chili kick",
        allergens_known="peanuts",
        voice=Voice.street,
    )
    result = generate_demo(req, has_image=False)
    assert result.original_dish == "Crispy Peanut Tofu Bao"
    assert any("peanut" in a.lower() for a in result.allergens)
    assert any("soy" in a.lower() or "wheat" in a.lower() for a in result.allergens)
    assert any("vegetarian" in d.lower() for d in result.dietary_tags)
    assert len(result.cards) == 2


def test_api_generate_and_history_lifecycle():
    # 1. Post to generate endpoint
    form_data = {
        "restaurant_name": "Casa Puebla",
        "cuisine": "Mexican / Puebla",
        "dish_name": "Mole Poblano",
        "category": "Chef's Specials",
        "price": "$22.00",
        "source_language": "Spanish",
        "target_languages": "English,Spanish",
        "ingredients": "ancho chiles, Mexican cacao, sesame, almonds",
        "story": "Celebration mole",
        "voice": "fine_dining",
        "force_demo": "true",
    }
    res = client.post("/api/generate", data=form_data)
    assert res.status_code == 200
    gen_result = res.json()
    assert gen_result["original_dish"] == "Mole Poblano"
    assert gen_result["id"] is not None
    dish_id = gen_result["id"]

    # 2. Check history contains it
    h_res = client.get("/api/history")
    assert h_res.status_code == 200
    history_items = h_res.json()["items"]
    assert len(history_items) >= 1
    saved_ids = [item["id"] for item in history_items]
    assert dish_id in saved_ids

    # 3. Filter by category
    cat_res = client.get("/api/history?category=Chef's Specials")
    assert cat_res.status_code == 200
    cat_items = cat_res.json()["items"]
    assert any(it["id"] == dish_id for it in cat_items)

    # 4. Export JSON
    exp_json = client.get("/api/export?format=json")
    assert exp_json.status_code == 200
    assert "restaurant_menu" in exp_json.json()
    assert exp_json.json()["count"] >= 1

    # 5. Export Markdown
    exp_md = client.get("/api/export?format=markdown")
    assert exp_md.status_code == 200
    assert "text/markdown" in exp_md.headers["content-type"]
    assert "Mole Poblano" in exp_md.text

    # 6. Delete item
    del_res = client.delete(f"/api/history/{dish_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] == dish_id

    # 7. Clear history
    clear_res = client.delete("/api/history")
    assert clear_res.status_code == 200
    assert clear_res.json()["cleared"] is True

    # 8. Check empty history
    empty_h = client.get("/api/history")
    assert len(empty_h.json()["items"]) == 0


def test_index_and_static_serving():
    res = client.get("/")
    assert res.status_code == 200
    assert "MenuForge" in res.text
    assert "qrcode.min.js" in res.text

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200

    res_css = client.get("/static/styles.css")
    assert res_css.status_code == 200

    res_qr = client.get("/static/qrcode.min.js")
    assert res_qr.status_code == 200


def test_sample_images_served():
    for img_name in ["kori-gassi.jpg", "mole-poblano.jpg", "banh-mi.jpg", "mapo-tofu.jpg", "doro-wat.jpg", "gua-bao.jpg"]:
        res = client.get(f"/samples/{img_name}")
        assert res.status_code == 200
        assert res.headers["content-type"] in ["image/jpeg", "image/jpg"]
