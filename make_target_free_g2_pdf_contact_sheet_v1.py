"""Create contact sheets for visual inspection of the rendered manuscript."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(r"D:\Projects\can_o_worms")
SRC = ROOT / "tmp" / "pdfs" / "target_free_g2_arxiv_render_v1"
OUT = ROOT / "tmp" / "pdfs" / "target_free_g2_arxiv_contact_sheets_v1"


def make_sheet(paths, target):
    if target.exists():
        raise FileExistsError(f"Retention rule: refusing to overwrite {target}")
    thumbs = []
    for path in paths:
        im = Image.open(path).convert("RGB")
        im.thumbnail((360, 466))
        thumbs.append((path, im.copy()))
    sheet = Image.new("RGB", (3 * 390, 2 * 505), "#d9d9d9")
    draw = ImageDraw.Draw(sheet)
    for i, (path, im) in enumerate(thumbs):
        x = (i % 3) * 390 + 15
        y = (i // 3) * 505 + 25
        sheet.paste(im, (x, y))
        draw.text((x, 5 + (i // 3) * 505), path.stem, fill="black")
    sheet.save(target)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = sorted(SRC.glob("page-*.png"))
    for start in range(0, len(pages), 6):
        make_sheet(pages[start : start + 6], OUT / f"pages-{start + 1:02d}-{min(start + 6, len(pages)):02d}.png")
    print("\n".join(str(x) for x in sorted(OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
