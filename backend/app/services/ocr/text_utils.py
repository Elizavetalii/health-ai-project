import re

from .constants import (
    CBC_INDICATORS,
    GARBAGE_MARKERS,
    LAB_INDICATOR_HINTS,
    MEDICAL_KEYWORDS,
    TABLE_MARKERS,
)


def normalize_ocr_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("\x0c", " ")
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = text.replace("|", " | ")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def trim_obvious_ocr_garbage(text: str) -> str:
    if not text.strip():
        return text

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        lowered = line.lower().strip()
        if any(marker in lowered for marker in GARBAGE_MARKERS):
            break
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def remove_obvious_noise_lines(text: str) -> str:
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        weird_count = len(re.findall(r"[©_=~`]+", stripped))
        if weird_count >= 3:
            continue

        if len(stripped) <= 2 and not re.search(r"\d", stripped):
            continue

        latin_garbage = re.findall(r"[A-Za-z]{4,}", stripped)
        if latin_garbage and not any(word.lower() in stripped.lower() for word in ["mcv", "mch", "mchc", "rdw"]):
            if not re.search(r"\d", stripped):
                continue

        cleaned.append(stripped)

    return "\n".join(cleaned).strip()


def looks_like_lab_line(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in LAB_INDICATOR_HINTS)


def line_has_number(line: str) -> bool:
    return bool(re.search(r"\d+[.,]?\d*", line))


def line_has_range(line: str) -> bool:
    return bool(re.search(r"\d+[.,]?\d*\s*-\s*\d+[.,]?\d*", line))


def line_has_unit(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in TABLE_MARKERS)


def score_ocr_text(text: str) -> int:
    if not text.strip():
        return -10_000

    lowered = text.lower()
    score = 0

    for keyword in MEDICAL_KEYWORDS:
        if keyword in lowered:
            score += 10

    digit_count = sum(ch.isdigit() for ch in text)
    score += min(digit_count, 350)

    for marker in TABLE_MARKERS:
        if marker in lowered:
            score += 14

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    score += min(len(lines), 140)

    structured_lines = 0

    for line in lines:
        ll = line.lower()
        has_indicator = any(hint in ll for hint in LAB_INDICATOR_HINTS)
        has_number = line_has_number(line)
        has_unit = line_has_unit(line)
        has_range = line_has_range(line)

        if has_indicator and has_number:
            score += 20
            structured_lines += 1

        if has_indicator and has_unit:
            score += 12

        if has_range:
            score += 10

        if "abs" in ll or "абс" in ll:
            score += 8

    score += structured_lines * 4

    weird_chars = re.findall(r"[^\w\s%.,:;()\/+\-*№а-яА-ЯёЁ]", text)
    score -= min(len(weird_chars) * 2, 220)

    word_count = len(re.findall(r"\b[\wа-яА-ЯёЁ]+\b", text))
    if word_count < 12:
        score -= 120

    return score


def fix_common_ocr_units(line: str) -> str:
    replacements = {
        "f/an": "г/дл",
        "r/an": "г/дл",
        "г/ап": "г/дл",
        "г/ал": "г/дл",
        "tym": "тыс",
        "тым": "тыс",
        "tyc": "тыс",
        "tyc.": "тыс.",
        "ас.": "абс.",
        "ac.": "абс.",
        "abc.": "абс.",
        "abc": "абс",
        "a6c.": "абс.",
        "мкп": "мкл",
        "мкпл": "мкл",
        "мкл.": "мкл",
        "тыс/мк": "тыс/мкл",
        "тыс/мл": "тыс/мкл",
        "тыс/мклл": "тыс/мкл",
        "млн/мк": "млн/мкл",
        "ммн/мкл": "млн/мкл",
        "гдл": "г/дл",
        "г дл": "г/дл",
        "фп": "фл",
        "nr": "пг",
        "ng": "пг",
        "тысиикл": "тыс/мкл",
        "тысииклл": "тыс/мкл",
        "тысиикл____": "тыс/мкл ",
    }

    fixed = line
    for wrong, correct in replacements.items():
        fixed = re.sub(re.escape(wrong), correct, fixed, flags=re.IGNORECASE)

    return fixed


def fix_common_ocr_indicators(line: str) -> str:
    replacements = {
        "гемогпобин": "гемоглобин",
        "гемоглобинн": "гемоглобин",
        "розраст": "возраст",
        "пейкоциты": "лейкоциты",
        "лимфоциты, ас.": "лимфоциты, абс.",
        "моноциты, ас.": "моноциты, абс.",
        "эозинофилы, ас.": "эозинофилы, абс.",
        "нейтрофилы, ас.": "нейтрофилы, абс.",
        "сегментоядерные ней": "сегментоядерные нейтрофилы",
        "палочкоядерные ней": "палочкоядерные нейтрофилы",
        "нейтрофилы (общ.число)": "нейтрофилы (общ. число)",
        "нейтрофилы (общ. число),": "нейтрофилы (общ. число), %",
        "mhs": "инз",
    }

    fixed = line
    for wrong, correct in replacements.items():
        fixed = re.sub(re.escape(wrong), correct, fixed, flags=re.IGNORECASE)

    return fixed


def fix_decimal_without_separator(line: str) -> str:
    lowered = line.lower()
    fixed = line

    if "лейкоц" in lowered or "wbc" in lowered:
        fixed = re.sub(r"\b([4-9])(\d{2})\b", r"\1.\2", fixed)

    if "mchc" in lowered:
        fixed = re.sub(r"\b(3[0-9])([0-9])\b", r"\1.\2", fixed)

    if re.search(r"\bmch\b", lowered) and "mchc" not in lowered:
        fixed = re.sub(r"\b([1-4]\d)(\d)\b", r"\1.\2", fixed)

    if "эритроц" in lowered or "rbc" in lowered:
        fixed = re.sub(r"\b([3-7])(\d{2})\b", r"\1.\2", fixed)

    if "гемоглобин" in lowered:
        fixed = re.sub(r"\b(1[0-9])([0-9])\b", r"\1.\2", fixed)

    return fixed


def normalize_lab_table_line(line: str) -> str:
    fixed = line.strip()
    fixed = fix_common_ocr_units(fixed)
    fixed = fix_common_ocr_indicators(fixed)
    fixed = fix_decimal_without_separator(fixed)

    fixed = re.sub(r"\s*%\s*уи\b", " г/дл", fixed, flags=re.IGNORECASE)
    fixed = re.sub(r"\s*\|\s*", " | ", fixed)
    fixed = re.sub(r"[ \t]+", " ", fixed)
    fixed = re.sub(r"_+", " ", fixed)

    return fixed.strip()


def normalize_lab_table_text(text: str) -> str:
    lines = text.splitlines()
    normalized_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            normalized_lines.append("")
            continue

        if looks_like_lab_line(stripped) or line_has_unit(stripped):
            normalized_lines.append(normalize_lab_table_line(stripped))
        else:
            normalized_lines.append(stripped)

    return "\n".join(normalized_lines).strip()


def merge_broken_lab_lines_soft(text: str) -> str:
    raw_lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in raw_lines if line]

    if not lines:
        return ""

    merged = []
    i = 0

    while i < len(lines):
        current = lines[i]

        if i + 1 < len(lines):
            nxt = lines[i + 1]

            current_is_indicator = looks_like_lab_line(current)
            current_has_number = line_has_number(current)
            next_has_number = line_has_number(nxt)
            next_has_unit = line_has_unit(nxt)
            next_has_range = line_has_range(nxt)

            if current_is_indicator and not current_has_number and (
                next_has_number or next_has_unit or next_has_range
            ):
                merged_line = normalize_lab_table_line(f"{current} {nxt}")
                merged.append(merged_line)
                i += 2
                continue

        merged.append(current)
        i += 1

    return "\n".join(merged).strip()


def extract_structured_lab_lines(text: str) -> list[dict]:
    results = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    seen = set()

    indicators_sorted = sorted(CBC_INDICATORS, key=len, reverse=True)

    for line in lines:
        lowered = line.lower()

        matched_indicator = None
        for indicator in indicators_sorted:
            if indicator in lowered:
                matched_indicator = indicator
                break

        if not matched_indicator:
            continue

        numbers = re.findall(r"\d+[.,]?\d*", line)

        key = (matched_indicator, line)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "raw_line": line,
            "indicator": matched_indicator,
            "numbers_found": numbers,
        })

    return results


def postprocess_extracted_text(text: str) -> str:
    text = normalize_ocr_text(text)
    text = normalize_lab_table_text(text)
    text = merge_broken_lab_lines_soft(text)
    text = remove_obvious_noise_lines(text)
    text = trim_obvious_ocr_garbage(text)
    text = normalize_ocr_text(text)
    return text.strip()