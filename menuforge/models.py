from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Voice(str, Enum):
    neighborhood = "neighborhood"
    fine_dining = "fine_dining"
    street = "street"
    family = "family"


class GenerateRequest(BaseModel):
    restaurant_name: str = Field(default="", description="Restaurant or stall name")
    cuisine: str = Field(default="", description="Cuisine / region, e.g. coastal Karnataka")
    dish_name: str = Field(..., min_length=1, description="Dish name in the source language")
    category: str = Field(default="Main Course", description="Menu section / course category")
    price: str = Field(default="", description="Dish price or seasonal note, e.g. $18.50")
    source_language: str = Field(default="auto", description="Language of the dish name")
    target_languages: list[str] = Field(
        default_factory=lambda: ["English", "Spanish"],
        description="Languages to translate into",
    )
    ingredients: str = Field(default="", description="Key ingredients / preparation notes")
    story: str = Field(default="", description="Origin story, spice level, serving notes")
    allergens_known: str = Field(default="", description="Known allergens if any")
    voice: Voice = Voice.neighborhood
    model: Optional[str] = None
    force_demo: bool = False


class LanguageCard(BaseModel):
    language: str
    dish_name: str
    short_blurb: str
    full_description: str


class MenuResult(BaseModel):
    id: Optional[int] = None
    restaurant_name: str
    cuisine: str = ""
    category: str = "Main Course"
    price: str = ""
    original_dish: str
    spice_level: str
    allergens: list[str]
    dietary_tags: list[str]
    pairings: list[str]
    cards: list[LanguageCard]
    qr_one_liner: str
    staff_pronunciation: str
    model_used: str
    mode: str
    offline_ready: bool = True
