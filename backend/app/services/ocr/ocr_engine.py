import pytesseract
from pytesseract import Output
from PIL import Image

from .text_utils import normalize_ocr_text, score_ocr_text


def run_ocr_string(image: Image.Image, config: str) -> str:
    try:
        text = pytesseract.image_to_string(
            image,
            lang="rus+eng",
            config=config,
        )
        return normalize_ocr_text(text)
    except Exception:
        return ""


def run_ocr_data(image: Image.Image, config: str) -> str:
    try:
        data = pytesseract.image_to_data(
            image,
            lang="rus+eng",
            config=config,
            output_type=Output.DICT,
        )
    except Exception:
        return ""

    rows = {}
    n = len(data.get("text", []))

    for i in range(n):
        token = (data["text"][i] or "").strip()
        conf_raw = data["conf"][i]

        if not token:
            continue

        try:
            conf = float(conf_raw)
        except Exception:
            conf = -1

        if conf < 20:
            continue

        key = (
            data["block_num"][i],
            data["par_num"][i],
            data["line_num"][i],
        )

        rows.setdefault(key, []).append((data["left"][i], token))

    lines = []
    for _, items in sorted(rows.items()):
        items.sort(key=lambda x: x[0])
        line = " ".join(token for _, token in items).strip()
        if line:
            lines.append(line)

    return normalize_ocr_text("\n".join(lines).strip())


def run_ocr_with_multiple_configs(image: Image.Image) -> list[str]:
    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 4",
        "--oem 3 --psm 11",
    ]

    results = []

    for config in configs:
        text = run_ocr_string(image, config)
        if text:
            results.append(text)

    return results

def choose_best_ocr_text(candidates: list[str]) -> str:
    unique_candidates = []
    seen = set()

    for text in candidates:
        normalized = normalize_ocr_text(text)
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_candidates.append(normalized)

    if not unique_candidates:
        return ""

    scored = [(score_ocr_text(text), text) for text in unique_candidates]
    scored.sort(key=lambda item: item[0], reverse=True)

    best_score, best_text = scored[0]
    print(f"OCR best score: {best_score}")

    return best_text