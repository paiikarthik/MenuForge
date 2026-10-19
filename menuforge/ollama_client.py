from __future__ import annotations

import base64
import json
import re
from typing import Any, Optional

import httpx

from .models import GenerateRequest, LanguageCard, MenuResult, Voice

DEFAULT_BASE = "http://127.0.0.1:11434"
VISION_CANDIDATES = (
    "llava:7b",
    "llava",
    "llama3.2-vision:11b",
    "llama3.2-vision",
    "moondream",
    "bakllava",
    "minicpm-v",
)
TEXT_CANDIDATES = (
    "llama3.2:3b",
    "llama3.2:1b",
    "llama3.2",
    "llama3.1:8b",
    "llama3.1",
    "qwen2.5:3b",
    "qwen2.5:7b",
    "qwen2.5:1.5b",
    "qwen2.5",
    "gemma2:2b",
    "gemma2:9b",
    "gemma2",
    "mistral:7b",
    "mistral",
    "phi3:mini",
    "phi3.5",
    "deepseek-r1:1.5b",
    "deepseek-r1:7b",
)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


class OllamaClient:
    def __init__(self, base_url: str = DEFAULT_BASE, timeout: float = 180.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]

    async def pick_model(
        self, preferred: Optional[str], need_vision: bool
    ) -> Optional[str]:
        models = await self.list_models()
        if not models:
            return None
        if preferred:
            for m in models:
                if m == preferred or m.lower().startswith(preferred.lower().split(":")[0]):
                    return m
        order = VISION_CANDIDATES + TEXT_CANDIDATES if need_vision else TEXT_CANDIDATES
        for cand in order:
            for m in models:
                if m.lower() == cand.lower() or m.lower().startswith(cand.lower()):
                    return m
        return models[0]

    async def generate_menu(
        self,
        req: GenerateRequest,
        image_b64: Optional[str],
    ) -> MenuResult:
        need_vision = bool(image_b64)
        model = await self.pick_model(req.model, need_vision=need_vision)
        if not model:
            raise RuntimeError("No Ollama models installed. Run: ollama pull llama3.2:3b")

        prompt = _build_prompt(req, has_image=need_vision)
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.45},
        }
        if image_b64:
            payload["images"] = [image_b64]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            raw = r.json().get("response", "")

        data = _extract_json(raw)
        return _to_result(data, req=req, model_used=model, mode="ollama")


def encode_image(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _build_prompt(req: GenerateRequest, has_image: bool) -> str:
    voice = {
        Voice.neighborhood: "Warm neighborhood bistro voice — welcoming, mouthwatering, approachable.",
        Voice.fine_dining: "Refined fine-dining voice — sensory precision, artisan craft, elegant.",
        Voice.street: "Vibrant street food stall voice — punchy, flavorful, energetic, concise.",
        Voice.family: "Heartfelt family kitchen voice — grandmother's cherished heritage, generous comfort.",
    }[req.voice]

    langs = ", ".join(req.target_languages) or "English"
    vision = (
        "Carefully observe the dish photo for true plating colors, textures, garnishes, and serving vessel. "
        "Do not hallucinate ingredients not seen in photo or mentioned in notes."
        if has_image
        else "No photo provided — rely on culinary knowledge and provided kitchen notes."
    )

    return f"""You are MenuForge, an expert culinary translator and menu copywriter for independent restaurants.
CRITICAL RULE: NEVER erase culinary heritage. Preserve authentic cultural dish names as proper nouns (e.g. keep 'Kori Gassi', 'Mole Poblano', 'Mapo Tofu', 'Bánh Mì', 'Doro Wat'); translate the meaning and appetizing culinary description rather than dumbing down to 'curry' or 'sandwich'.

{vision}
Voice profile: {voice}
Restaurant name: {req.restaurant_name or '(Independent Kitchen)'}
Cuisine / Region: {req.cuisine or '(Heritage)'}
Course Category: {req.category or 'Main Course'}
Price: {req.price or '(Market Price)'}
Dish name ({req.source_language}): {req.dish_name}
Key ingredients & prep: {req.ingredients or '(Chef seasonal selection)'}
Culinary origin & story: {req.story or '(House heritage specialty)'}
Known allergens: {req.allergens_known or '(carefully infer from ingredients)'}
Target translation languages: {langs}

Respond with ONLY valid JSON with this schema:
{{
  "spice_level": "none | mild | medium | hot | varies",
  "allergens": ["list known or likely allergens, e.g. dairy, peanuts, shellfish, gluten, soy, eggs"],
  "dietary_tags": ["e.g. vegetarian, vegan option, gluten-free, halal-suitable"],
  "pairings": ["2-3 ideal drink, side, or wine pairings"],
  "staff_pronunciation": "intuitive phonetic pronunciation guide for servers (e.g. KO-ri GAH-see)",
  "qr_one_liner": "punchy 1-sentence teaser for table QR codes and sidewalk chalkboard",
  "cards": [
    {{
      "language": "English",
      "dish_name": "Authentic dish name with cultural subtitle if helpful",
      "short_blurb": "maximum 20 words for menu chalkboard or table tent",
      "full_description": "2-4 evocative sentences for printed dinner menu"
    }}
  ]
}}

Generate exactly one card per target language listed. Use proper native accents and scripts where appropriate.
"""


def _to_result(
    data: dict[str, Any], req: GenerateRequest, model_used: str, mode: str
) -> MenuResult:
    raw_cards = data.get("cards") or []
    cards: list[LanguageCard] = []
    for c in raw_cards:
        if not isinstance(c, dict):
            continue
        cards.append(
            LanguageCard(
                language=str(c.get("language") or "English"),
                dish_name=str(c.get("dish_name") or req.dish_name).strip(),
                short_blurb=str(c.get("short_blurb") or "").strip(),
                full_description=str(c.get("full_description") or "").strip(),
            )
        )
    if not cards:
        cards = [
            LanguageCard(
                language="English",
                dish_name=req.dish_name,
                short_blurb=f"House specialty — {req.story or 'ask your server for today details'}.",
                full_description=req.story or req.ingredients or req.dish_name,
            )
        ]

    def _list(val: Any) -> list[str]:
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        if isinstance(val, str) and val.strip():
            return [x.strip() for x in val.split(",") if x.strip()]
        return []

    return MenuResult(
        restaurant_name=req.restaurant_name or "Independent Kitchen",
        cuisine=req.cuisine or "Heritage",
        category=req.category or "Main Course",
        price=req.price or "",
        original_dish=req.dish_name,
        spice_level=str(data.get("spice_level") or "varies").strip(),
        allergens=_list(data.get("allergens")),
        dietary_tags=_list(data.get("dietary_tags")),
        pairings=_list(data.get("pairings")),
        cards=cards,
        qr_one_liner=str(data.get("qr_one_liner") or "").strip(),
        staff_pronunciation=str(data.get("staff_pronunciation") or req.dish_name).strip(),
        model_used=model_used,
        mode=mode,
        offline_ready=True,
    )
