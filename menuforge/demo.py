"""Offline demo engine with real-world culinary fixtures and intelligent heuristics."""

from __future__ import annotations

import re
from typing import Optional

from .models import GenerateRequest, LanguageCard, MenuResult, Voice


# Authentic, culturally respectful fixtures for signature world dishes
FIXTURES: dict[str, dict] = {
    "kori gassi": {
        "cuisine": "Mangalorean / Coastal Karnataka",
        "category": "Mains & Curries",
        "price": "₹420 / $18.50",
        "spice": "hot",
        "allergens": ["dairy (if finished with ghee)", "coconut"],
        "dietary": ["gluten-free", "contains poultry", "halal-suitable"],
        "pairings": ["neer dosa (lacy rice crepes)", "boiled red rice", "kokum sol kadhi", "tender coconut water"],
        "pronounce": "KO-ri GAH-see",
        "cards": {
            "English": (
                "Kori Gassi",
                "Mangalorean chicken curry slow-simmered in roasted coconut & Byadgi chili gravy.",
                "A coastal Karnataka heritage classic: tender country chicken simmered in an aromatic gravy of freshly grated roasted coconut, Byadgi chilies, coriander seeds, and fresh curry leaves, balanced with sour tamarind. Traditionally paired with paper-thin neer dosa or boiled red rice.",
            ),
            "Spanish": (
                "Kori Gassi (Curry de pollo de Mangalore)",
                "Curry costero de pollo en salsa aterciopelada de coco tostado y chile Byadgi.",
                "Clásico ancestral de la costa de Karnataka: pollo tierno cocinado a fuego lento en una rica salsa de coco tostado en sartén de hierro, chiles Byadgi aromáticos y hojas frescas de curry, con un toque de tamarindo. Servido tradicionalmente con neer dosa o arroz rojo al vapor.",
            ),
            "Hindi": (
                "कोरी गस्सी (Kori Gassi)",
                "मैंगलोरियन चिकन करी — भुने नारियल और ब्याडगी मिर्च की गाढ़ी ग्रेवी में।",
                "तटीय कर्नाटक की ऐतिहासिक और पारंपरिक चिकन करी: धीमी आंच पर भुने हुए ताजे नारियल, ब्याडगी लाल मिर्च और ताजी कढ़ी पत्तों की खुशबूदार ग्रेवी में पकाया गया चिकन। पारंपरिक रूप से नीर डोसा या लाल चावल के साथ परोसा जाता है।",
            ),
            "French": (
                "Kori Gassi",
                "Curry de poulet de Mangalore à la noix de coco grillée et piments Byadgi.",
                "Grand classique de la côte de Karnataka : morceaux de poulet mijotés délicatement dans une sauce veloutée de noix de coco fraîchement torréfiée, relevée de piments Byadgi et de feuilles de curry fraîches, avec une pointe de tamarin. Servi avec crêpes neer dosa.",
            ),
        },
    },
    "mole poblano": {
        "cuisine": "Mexican / Puebla",
        "category": "Chef's Specials",
        "price": "$22.00 / 380 MXN",
        "spice": "medium",
        "allergens": ["sesame", "tree nuts (almonds)", "gluten (plantain/pan dulce thickener)"],
        "dietary": ["contains poultry", "dairy-free option", "celebration dish"],
        "pairings": ["arroz rojo mexicano", "fresh handmade corn tortillas", "agua de jamaica", "mezcal artesanal"],
        "pronounce": "MO-leh po-BLAH-no",
        "cards": {
            "English": (
                "Mole Poblano",
                "Heritage slow-simmered Puebla mole of dried chiles, toasted nuts, and Mexican cacao.",
                "Mexico's celebratory crown jewel: slow-simmered over three days from ancho, pasilla, and mulato chiles, toasted sesame, Mexican chocolate, cloves, and warm spices over tender poultry. Complex, smoky, deeply savory, and never cloyingly sweet.",
            ),
            "Spanish": (
                "Mole Poblano Artesanal",
                "Guiso ceremonial de chiles secos, semillas tostadas y chocolate mexicano.",
                "El gran clásico festivo de Puebla: preparado pacientemente con chiles ancho, mulato y pasilla, semillas de ajonjolí tostadas, almendras y un toque de chocolate de metate. De perfil profundo, complejo y sutilmente ahumado, bañado sobre tierna pieza de ave.",
            ),
            "French": (
                "Mole Poblano Traditionnel",
                "Sauce cérémonielle de Puebla aux piments doux séchés, sésame et cacao mexicain.",
                "Joyau gastronomique de Puebla : sauce d'une complexité légendaire mijotée lentement à base de piments séchés, d'amandes grillées, d'épices douces et d'une touche de cacao pur. Servie sur volaille tendre avec tortillas de maïs fraîches.",
            ),
        },
    },
    "banh mi": {
        "cuisine": "Vietnamese / Saigon Street Food",
        "category": "Street Bites & Sandwiches",
        "price": "$11.50 / 95,000 VND",
        "spice": "mild (jalapeño on request)",
        "allergens": ["wheat / gluten", "soy", "egg (house mayonnaise)"],
        "dietary": ["contains pork & poultry liver", "dairy-free"],
        "pairings": ["cà phê sữa đá (Vietnamese iced coffee)", "chilled jasmine green tea", "pickled lotus root"],
        "pronounce": "bun MEE dak bee-ET",
        "cards": {
            "English": (
                "Bánh Mì Đặc Biệt",
                "Crispy Saigon baguette loaded with slow-roasted pork, rich liver pâté & crisp pickles.",
                "The pride of Saigon street food: ultra-crisp, featherlight French-Vietnamese baguette spread with house-whipped liver pâté and egg yolk mayo, stacked with roasted pork, cucumber spears, cilantro, and sweet-tart pickled daikon and carrots.",
            ),
            "Spanish": (
                "Bánh Mì Đặc Biệt (Baguette vietnamita)",
                "Baguette crujiente con cerdo asado, paté artesanal, hierbas frescas y encurtidos.",
                "El icono callejero de Saigón: baguette ligera de corteza extra crujiente, rellena de paté de la casa, finas lonchas de cerdo laqueado, pepino fresco, cilantro y un toque vibrante de zanahoria y rábano daikon encurtidos.",
            ),
            "French": (
                "Bánh Mì Spécial Saïgon",
                "Baguette croustillante garnie de porc rôti, pâté maison et pickles croquants.",
                "L'incontournable sandwich de Saïgon : pain baguette à la mie aérienne et croûte croustillante, tartiné de pâté savoureux et mayonnaise maison, garni de porc rôti, coriandre fraîche, concombres et légumes aigre-doux marinés.",
            ),
        },
    },
    "mapo tofu": {
        "cuisine": "Sichuan / Chengdu",
        "category": "Mains & Curries",
        "price": "$16.00 / ¥58",
        "spice": "hot (málà / spicy & numbing)",
        "allergens": ["soy (tofu & fermented broad beans)", "sesame"],
        "dietary": ["vegetarian / vegan optional", "dairy-free", "contains Sichuan peppercorn"],
        "pairings": ["steamed jasmine rice", "cold Tsingtao lager", "chrysanthemum iced tea"],
        "pronounce": "MAH-poh DOH-foo",
        "cards": {
            "English": (
                "Mapo Tofu (麻婆豆腐)",
                "Silken tofu in fiery Pixian fermented chile-bean paste and numbing Sichuan peppercorn.",
                "Chengdu's legendary masterwork: tender cubes of silken tofu wok-braised in aged Pixian doubanjiang, fermented black beans, and fragrant chili oil, finished with a generous dusting of hand-toasted Sichuan flower pepper for the authentic 'málà' numbing thrill.",
            ),
            "Spanish": (
                "Mapo Tofu (麻婆豆腐)",
                "Tofu sedoso en pasta fermentada de chile de Pixian y pimienta de Sichuan.",
                "Obra maestra de la cocina de Chengdu: cubos de tofu sedoso salteados al wok con pasta fermentada de habas y chiles de Pixian, aceite aromático de chile y un toque generoso de pimienta de Sichuan tostada que aporta el auténtico cosquilleo 'málà'.",
            ),
            "French": (
                "Mapo Tofu (麻婆豆腐)",
                "Tofu soyeux braisé au wok dans une sauce fermentée de piments de Pixian et poivre du Sichuan.",
                "Plat emblématique de Chengdu : cubes de tofu soyeux cuisinés au wok dans une sauce riche de pâte de fèves fermentées de Pixian et d'huile pimentée, sublimés par le parfum boisé et anesthésiant du poivre rouge du Sichuan fraîchement moulu.",
            ),
        },
    },
    "doro wat": {
        "cuisine": "Ethiopian / Addis Ababa",
        "category": "Mains & Curries",
        "price": "$21.00 / 480 ETB",
        "spice": "hot (slow-simmered berbere)",
        "allergens": ["dairy (niter kibbeh spiced butter)", "egg (hard-cooked egg)"],
        "dietary": ["gluten-free with 100% teff injera", "contains poultry", "halal-suitable"],
        "pairings": ["warm teff injera", "ayib (fresh cottage cheese)", "Tej (Ethiopian honey wine)"],
        "pronounce": "DOH-roh WAHT",
        "cards": {
            "English": (
                "Doro Wat",
                "Slow-braised Ethiopian chicken stew in caramelized red onions, berbere & spiced butter.",
                "The centerpiece of Ethiopian feast culture: farm chicken slow-braised for hours in sweet caramelized red onions, sun-dried berbere chili spice blend, garlic, ginger, and aromatic herbal clarified butter (niter kibbeh), served with a spice-infused hard-boiled egg atop sour teff injera.",
            ),
            "Spanish": (
                "Doro Wat (Estofado etíope)",
                "Pollo estofado lentamente con cebollas caramelizadas, especias berbere y mantequilla aromática.",
                "Plato festivo por excelencia de Etiopía: pollo tierno estofado pacientemente en una reducción untuosa de cebollas rojas, mezcla de especias berbere y mantequilla clarificada niter kibbeh. Se sirve con un huevo cocido infusionado y pan fermentado injera.",
            ),
            "French": (
                "Doro Wat Traditionnel",
                "Mijoté de poulet éthiopien aux oignons fondants, mélange berbéré et beurre épicé.",
                "Plat national et festif d'Éthiopie : morceaux de poulet mijotés de longues heures dans une réduction d'oignons rouges, parfumés au mélange d'épices berbéré et au beurre clarifié niter kibbeh. Accompagné d'un œuf dur mariné et d'une crêpe d'injera au teff.",
            ),
        },
    },
    "gua bao": {
        "cuisine": "Taiwanese / Night Market",
        "category": "Street Bites & Sandwiches",
        "price": "$12.00 / 120 TWD",
        "spice": "mild",
        "allergens": ["peanuts", "wheat / gluten", "soy", "sesame"],
        "dietary": ["contains pork", "contains peanuts", "dairy-free"],
        "pairings": ["Taiwanese Dong Ding oolong tea", "apple cider soda", "winter melon iced tea"],
        "pronounce": "GWAH-bow",
        "cards": {
            "English": (
                "Gua Bao (割包)",
                "Steamed lotus leaf bun filled with red-braised pork belly, pickled greens & crushed peanut sugar.",
                "The beloved 'Taiwanese burger' of Taipei night markets: an airy, cloud-like steamed bun cradling a melt-in-your-mouth slab of five-spice soy-braised pork belly, balanced with tart fermented mustard greens, fresh coriander, and sweet roasted peanut powder.",
            ),
            "Spanish": (
                "Gua Bao (割包)",
                "Panecillo al vapor con panceta de cerdo braseada, mostaza encurtida y polvo de cacahuete.",
                "El bocado callejero estrella de Taiwán: esponjoso panecillo blanco al vapor relleno de tierna panceta glaseada en cinco especias y soja, contrastada con hojas de mostaza fermentada, cilantro fresco y cacahuete tostado dulce.",
            ),
            "French": (
                "Gua Bao Taïwanais (割包)",
                "Brioche vapeur farcie de poitrine de porc confite, moutarde marinée et poudre de cacahuète.",
                "Le sandwich vapeur culte des marchés de nuit de Taipei : un pain lotus blanc ultra moelleux garni d'une tranche fondante de poitrine de porc mijotée aux cinq-épices, relevée de moutarde fermentée croquante, coriandre et cacahuètes grillées caramélisées.",
            ),
        },
    },
}


ALLERGEN_PATTERNS = {
    "dairy": r"\b(milk|cream|butter|ghee|cheese|paneer|yogurt|curd|whey|casein)\b",
    "peanuts": r"\b(peanut|groundnut)\b",
    "tree nuts": r"\b(almond|cashew|walnut|pistachio|pecan|hazelnut|macadamia|pine nut)\b",
    "shellfish": r"\b(shrimp|prawn|crab|lobster|calamari|squid|clam|mussel|oyster|scallop)\b",
    "fish": r"\b(fish|salmon|tuna|cod|anchovy|halibut|sea bass|tilapia|snapper)\b",
    "wheat / gluten": r"\b(wheat|flour|bread|baguette|pasta|noodle|bun|seitan|soy sauce|semolina|barley)\b",
    "soy": r"\b(soy|tofu|edamame|miso|tamari|tempeh|doubanjiang)\b",
    "sesame": r"\b(sesame|tahini)\b",
    "egg": r"\b(egg|mayo|mayonnaise|aioli)\b",
}


def _norm(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", "", s.lower()).split())


def _infer_allergens(ingredients: str, user_allergens: str) -> list[str]:
    found: list[str] = []
    text = f"{ingredients} {user_allergens}".lower()
    for allergen, pattern in ALLERGEN_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(allergen)
    if user_allergens:
        for extra in user_allergens.split(","):
            val = extra.strip()
            if val and val.lower() not in [f.lower() for f in found]:
                found.append(val)
    if not found:
        found = ["kitchen check: no standard allergens declared"]
    return found[:6]


def _infer_dietary(ingredients: str, allergens: list[str]) -> list[str]:
    text = ingredients.lower()
    meat = bool(re.search(r"\b(chicken|beef|pork|lamb|goat|turkey|duck|bacon|meat|pâté|veal)\b", text))
    seafood = bool(re.search(r"\b(fish|shrimp|prawn|crab|lobster|clam|mussel|squid)\b", text))
    tags: list[str] = []
    if meat or seafood:
        tags.append("contains meat/seafood" if (meat and seafood) else ("contains poultry/meat" if meat else "contains seafood"))
    else:
        tags.append("vegetarian")
        dairy_or_egg = any("dairy" in a.lower() or "egg" in a.lower() for a in allergens)
        if not dairy_or_egg and not bool(re.search(r"\b(honey|gelatin)\b", text)):
            tags.append("vegan")
    if not any("gluten" in a.lower() or "wheat" in a.lower() for a in allergens):
        tags.append("gluten-free friendly")
    tags.append("freshly prepared daily")
    return tags[:4]


def _infer_spice(ingredients: str, story: str) -> str:
    combined = f"{ingredients} {story}".lower()
    if re.search(r"\b(ghost|habanero|reaper|bird'?s eye|byadgi|sichuan|berbere|thai chili|very spicy|extra spicy|fire)\b", combined):
        return "hot"
    if re.search(r"\b(jalapeño|jalapeno|poblano|chipotle|chili|chile|peppercorn|medium|spiced|ginger)\b", combined):
        return "medium"
    if re.search(r"\b(mild|sweet|cream|honey|gentle|no chili)\b", combined):
        return "mild"
    return "varies by guest preference"


def _infer_pronunciation(dish: str) -> str:
    # Heuristic syllable generator
    words = dish.split()
    parts = []
    for w in words:
        clean = re.sub(r"[^\w]", "", w)
        if len(clean) <= 4:
            parts.append(clean.upper())
        else:
            mid = len(clean) // 2
            parts.append(f"{clean[:mid].upper()}-{clean[mid:].lower()}")
    return " ".join(parts)


def generate_demo(req: GenerateRequest, has_image: bool) -> MenuResult:
    key = _norm(req.dish_name)
    fixture = None
    for name, data in FIXTURES.items():
        n_clean = _norm(name)
        if n_clean in key or key in n_clean:
            fixture = data
            break

    langs = req.target_languages or ["English"]
    voice_label = {
        Voice.neighborhood: "neighborhood kitchen favorite",
        Voice.fine_dining: "chef's slow-crafted specialty",
        Voice.street: "bustling street-side classic",
        Voice.family: "grandmother's cherished family recipe",
    }[req.voice]

    cards: list[LanguageCard] = []

    if fixture:
        category = req.category or fixture.get("category", "Main Course")
        price = req.price or fixture.get("price", "")
        cuisine = req.cuisine or fixture.get("cuisine", "")
        spice = fixture["spice"]
        allergens = list(fixture["allergens"])
        dietary = list(fixture["dietary"])
        pairings = list(fixture["pairings"])
        pronounce = fixture["pronounce"]

        for lang in langs:
            pack = fixture["cards"].get(lang) or fixture["cards"].get("English")
            name, short, full = pack
            if lang not in fixture["cards"] and lang != "English":
                short = f"{short} ({lang} draft)"
                full = f"[{lang}] {full}"
            cards.append(
                LanguageCard(
                    language=lang,
                    dish_name=name,
                    short_blurb=short,
                    full_description=full,
                )
            )
        qr_blurb = f"{req.restaurant_name or 'House Special'}: {req.dish_name} — {voice_label}."
    else:
        category = req.category or "Main Course"
        price = req.price or ""
        cuisine = req.cuisine or "House Heritage"
        ingredients = req.ingredients or "seasonal garden produce and chef's spice pantry"
        story = req.story or f"A signature {voice_label} celebrating regional flavors."
        allergens = _infer_allergens(ingredients, req.allergens_known)
        dietary = _infer_dietary(ingredients, allergens)
        spice = _infer_spice(ingredients, story)
        pronounce = _infer_pronunciation(req.dish_name)
        pairings = ["steamed fragrant rice or artisanal warm bread", "house craft iced tea or cellar wine pairing"]
        photo_cue = "Plating accented with vibrant color and garnish observed in your kitchen photo. " if has_image else ""

        for lang in langs:
            l_lower = lang.lower()
            if l_lower.startswith("spanish") or "español" in l_lower:
                cards.append(
                    LanguageCard(
                        language=lang,
                        dish_name=req.dish_name,
                        short_blurb=f"Especialidad de la casa: {req.dish_name}.",
                        full_description=(
                            f"{req.dish_name}. {story} Elaborado con {ingredients}. "
                            f"{photo_cue}Consulta a nuestro personal para maridajes y opciones dietéticas."
                        ),
                    )
                )
            elif l_lower.startswith("hindi"):
                cards.append(
                    LanguageCard(
                        language=lang,
                        dish_name=f"{req.dish_name}",
                        short_blurb=f"रसोई की खास पेशकश: {req.dish_name}।",
                        full_description=(
                            f"{req.dish_name} — {story} मुख्य सामग्री: {ingredients}। "
                            f"{photo_cue}पारंपरिक स्वाद और शुद्ध सामग्री से तैयार। अधिक जानकारी के लिए स्टाफ़ से संपर्क करें।"
                        ),
                    )
                )
            elif l_lower.startswith("french") or "français" in l_lower:
                cards.append(
                    LanguageCard(
                        language=lang,
                        dish_name=req.dish_name,
                        short_blurb=f"Spécialité du chef : {req.dish_name}.",
                        full_description=(
                            f"{req.dish_name}. {story} Préparé avec {ingredients}. "
                            f"{photo_cue}Demandez conseil à votre serveur pour les accords mets et vins."
                        ),
                    )
                )
            elif l_lower.startswith("german") or "deutsch" in l_lower:
                cards.append(
                    LanguageCard(
                        language=lang,
                        dish_name=req.dish_name,
                        short_blurb=f"Haus-Spezialität: {req.dish_name}.",
                        full_description=(
                            f"{req.dish_name}. {story} Zubereitet mit {ingredients}. "
                            f"{photo_cue}Fragen Sie unser Personal nach passenden Getränken."
                        ),
                    )
                )
            else:
                cards.append(
                    LanguageCard(
                        language=lang,
                        dish_name=req.dish_name,
                        short_blurb=f"{req.dish_name} — {voice_label}.",
                        full_description=(
                            f"{req.dish_name}. {story} Prepared with {ingredients}. "
                            f"{photo_cue}Served hot; consult your server for seasonal pairings and dietary accommodations."
                        ),
                    )
                )
        qr_blurb = f"{req.dish_name} ({price}): {story[:120]}"

    if req.allergens_known:
        user_list = [a.strip() for a in req.allergens_known.split(",") if a.strip()]
        for u in user_list:
            if u not in allergens:
                allergens.insert(0, u)

    return MenuResult(
        restaurant_name=req.restaurant_name or "Independent Kitchen",
        cuisine=cuisine,
        category=category,
        price=price,
        original_dish=req.dish_name,
        spice_level=spice,
        allergens=allergens[:6],
        dietary_tags=dietary[:6],
        pairings=pairings[:4],
        cards=cards,
        qr_one_liner=qr_blurb[:160],
        staff_pronunciation=pronounce,
        model_used="demo-engine (zero-download offline fixtures)",
        mode="demo",
        offline_ready=True,
    )
