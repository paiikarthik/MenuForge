"""Generate appetizing culinary badge placeholder images for MenuForge sample dishes."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "static" / "samples"


def _font(size: int):
    for name in (
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/seguisb.ttf",
        "DejaVuSans.ttf",
        "Arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def kori():
    img = Image.new("RGB", (900, 700), "#1a1210")
    d = ImageDraw.Draw(img)
    # Clay pot rim & coconut gravy
    d.ellipse((220, 160, 680, 580), fill="#8b3a1f", outline="#c4a35a", width=6)
    d.ellipse((270, 210, 630, 530), fill="#5c2414")
    d.ellipse((340, 270, 560, 470), fill="#d4a574")
    # Fresh curry leaves & red chili accents
    d.ellipse((380, 310, 440, 350), fill="#2f6b55")
    d.ellipse((470, 370, 510, 410), fill="#a82e1c")
    d.text((45, 45), "MenuForge · Kori Gassi", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Mangalorean Roasted Coconut & Byadgi Chili Curry", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def mole():
    img = Image.new("RGB", (900, 700), "#120e0a")
    d = ImageDraw.Draw(img)
    # Deep obsidian-chocolate mole cazuela
    d.ellipse((220, 160, 680, 580), fill="#2a160d", outline="#c4a35a", width=6)
    d.ellipse((280, 220, 620, 520), fill="#1a0d07")
    # Toasted sesame sprinkle
    for pos in [
        (400, 310), (430, 290), (470, 340), (410, 370), (490, 320),
        (440, 400), (370, 350), (510, 370), (460, 430), (390, 420)
    ]:
        d.ellipse((pos[0], pos[1], pos[0] + 8, pos[1] + 8), fill="#e8dcc8")
    d.text((45, 45), "MenuForge · Mole Poblano", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Puebla Dried Chiles, Toasted Sesame & Artisanal Cacao", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def banh():
    img = Image.new("RGB", (900, 700), "#17201a")
    d = ImageDraw.Draw(img)
    # Crispy golden baguette silhouette
    d.polygon([(180, 380), (720, 290), (740, 380), (200, 470)], fill="#e8d8b5", outline="#c4a35a", width=5)
    # Char siu pork & pâté layer
    d.line([(220, 415), (700, 335)], fill="#7a2416", width=14)
    # Pickled daikon & carrot ribbons
    d.line([(230, 428), (690, 348)], fill="#e06d3b", width=8)
    # Crisp fresh cilantro sprigs
    d.line([(240, 440), (680, 360)], fill="#2f6b55", width=9)
    d.text((45, 45), "MenuForge · Bánh Mì Đặc Biệt", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Saigon Crusty Baguette, Pork Pâté & Bright Pickles", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def mapo():
    img = Image.new("RGB", (900, 700), "#1c0d0a")
    d = ImageDraw.Draw(img)
    # Sizzling wok & crimson chili oil
    d.ellipse((220, 160, 680, 580), fill="#7a1811", outline="#c4a35a", width=6)
    d.ellipse((270, 210, 630, 530), fill="#4d0e0a")
    # Silken tofu cubes
    for (x, y) in [(340, 290), (450, 280), (380, 380), (490, 370), (420, 440)]:
        d.rectangle((x, y, x + 55, y + 45), fill="#f0eae1", outline="#c4a35a", width=2)
    # Scallion greens
    d.ellipse((370, 330, 395, 345), fill="#2f6b55")
    d.ellipse((480, 340, 505, 355), fill="#2f6b55")
    d.ellipse((430, 410, 455, 425), fill="#2f6b55")
    d.text((45, 45), "MenuForge · Mapo Tofu (麻婆豆腐)", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Chengdu Silken Tofu, Pixian Doubanjiang & Sichuan Peppercorn", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def doro():
    img = Image.new("RGB", (900, 700), "#18100c")
    d = ImageDraw.Draw(img)
    # Porous teff injera disc
    d.ellipse((200, 150, 700, 590), fill="#c9ab7b", outline="#c4a35a", width=5)
    # Dark berbere stew center
    d.ellipse((290, 230, 610, 510), fill="#420f09")
    # Spiced hard-boiled egg cut in half
    d.ellipse((410, 330, 490, 410), fill="#f7f2dc", outline="#992b1a", width=3)
    d.ellipse((430, 350, 470, 390), fill="#f0ad32")
    d.text((45, 45), "MenuForge · Doro Wat", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Ethiopian Slow-Braised Berbere Chicken with Teff Injera", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def gua():
    img = Image.new("RGB", (900, 700), "#1a1614")
    d = ImageDraw.Draw(img)
    # Steamed white lotus bao bun
    d.ellipse((240, 200, 660, 540), fill="#f5f0e6", outline="#c4a35a", width=5)
    # Braised pork belly slab
    d.rectangle((310, 320, 590, 410), fill="#381b12")
    d.rectangle((310, 320, 590, 345), fill="#823c22")
    # Fermented greens & peanut powder
    d.line([(320, 410), (580, 410)], fill="#2f6b55", width=12)
    for px in [350, 390, 430, 470, 510, 540]:
        d.ellipse((px, 310, px + 10, 320), fill="#d49a55")
    d.text((45, 45), "MenuForge · Gua Bao (割包)", fill="#e8efe8", font=_font(32))
    d.text((45, 85), "Taiwanese Lotus Bun with Red-Braised Pork Belly & Crushed Peanuts", fill="#c4a35a", font=_font(20))
    d.text((45, 635), "100% Local · Confidential Family Recipe", fill="#8aa396", font=_font(18))
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.jpg"):
        try:
            old.unlink()
        except Exception:
            pass
    kori().save(OUT / "kori-gassi.jpg", quality=92)
    mole().save(OUT / "mole-poblano.jpg", quality=92)
    banh().save(OUT / "banh-mi.jpg", quality=92)
    mapo().save(OUT / "mapo-tofu.jpg", quality=92)
    doro().save(OUT / "doro-wat.jpg", quality=92)
    gua().save(OUT / "gua-bao.jpg", quality=92)
    print(f"Generated 6 sample dish artworks in {OUT}")


if __name__ == "__main__":
    main()
