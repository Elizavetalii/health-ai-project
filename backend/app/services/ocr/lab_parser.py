import re
from typing import Any


CBC_CANONICAL_MAP = {
    "гематокрит": "Гематокрит",
    "гемоглобин": "Гемоглобин",
    "эритроциты": "Эритроциты",
    "mcv": "MCV",
    "rdw": "RDW",
    "mch": "MCH",
    "mchc": "MCHC",
    "тромбоциты": "Тромбоциты",
    "лейкоциты": "Лейкоциты",

    "палочкоядерные": "Палочкоядерные нейтрофилы",
    "палочкоядерные нейтрофилы": "Палочкоядерные нейтрофилы",

    "сегментоядерные": "Сегментоядерные нейтрофилы",
    "сегментоядерные нейтрофилы": "Сегментоядерные нейтрофилы",

    "нейтрофилы (общ. число)": "Нейтрофилы (общ. число), %",
    "лимфоциты, %": "Лимфоциты, %",
    "моноциты, %": "Моноциты, %",
    "эозинофилы, %": "Эозинофилы, %",
    "базофилы, %": "Базофилы, %",

    "нейтрофилы, абс.": "Нейтрофилы, абс.",
    "лимфоциты, абс.": "Лимфоциты, абс.",
    "моноциты, абс.": "Моноциты, абс.",
    "эозинофилы, абс.": "Эозинофилы, абс.",
    "базофилы, абс.": "Базофилы, абс.",

    "промиелоциты": "Промиелоциты",
    "миелоциты": "Миелоциты",
    "метамиелоциты": "Метамиелоциты",
    "плазматические клетки": "Плазматические клетки",
    "активированные лимфоциты": "Активированные лимфоциты",
    "атипичные мононуклеары": "Атипичные мононуклеары",
    "пролимфоциты": "Пролимфоциты",
    "бласты": "Бласты",
    "нормоциты": "Нормоциты",

    "соэ": "СОЭ",
    "соэ (по вестергрену)": "СОЭ",
}

EXPECTED_UNITS = {
    "Гематокрит": "%",
    "Гемоглобин": "г/дл",
    "Эритроциты": "млн/мкл",
    "MCV": "фл",
    "RDW": "%",
    "MCH": "пг",
    "MCHC": "г/дл",
    "Тромбоциты": "тыс/мкл",
    "Лейкоциты": "тыс/мкл",

    "Палочкоядерные нейтрофилы": "%",
    "Сегментоядерные нейтрофилы": "%",
    "Нейтрофилы (общ. число), %": "%",
    "Лимфоциты, %": "%",
    "Моноциты, %": "%",
    "Эозинофилы, %": "%",
    "Базофилы, %": "%",

    "Нейтрофилы, абс.": "тыс/мкл",
    "Лимфоциты, абс.": "тыс/мкл",
    "Моноциты, абс.": "тыс/мкл",
    "Эозинофилы, абс.": "тыс/мкл",
    "Базофилы, абс.": "тыс/мкл",

    "Промиелоциты": "%",
    "Миелоциты": "%",
    "Метамиелоциты": "%",
    "Плазматические клетки": "%",
    "Активированные лимфоциты": "%",
    "Атипичные мононуклеары": "%",
    "Пролимфоциты": "%",
    "Бласты": "%",
    "Нормоциты": "кл/100 лейк.",
    "СОЭ": "мм/ч",
}

PLAUSIBLE_RANGES = {
    "Гематокрит": (10.0, 70.0),
    "Гемоглобин": (5.0, 25.0),
    "Эритроциты": (2.0, 8.0),
    "MCV": (50.0, 130.0),
    "RDW": (5.0, 30.0),
    "MCH": (10.0, 40.0),
    "MCHC": (20.0, 45.0),
    "Тромбоциты": (10.0, 1000.0),
    "Лейкоциты": (0.1, 100.0),

    "Палочкоядерные нейтрофилы": (0.0, 20.0),
    "Сегментоядерные нейтрофилы": (0.0, 100.0),
    "Нейтрофилы (общ. число), %": (0.0, 100.0),
    "Лимфоциты, %": (0.0, 100.0),
    "Моноциты, %": (0.0, 100.0),
    "Эозинофилы, %": (0.0, 100.0),
    "Базофилы, %": (0.0, 20.0),

    "Нейтрофилы, абс.": (0.0, 20.0),
    "Лимфоциты, абс.": (0.0, 20.0),
    "Моноциты, абс.": (0.0, 20.0),
    "Эозинофилы, абс.": (0.0, 20.0),
    "Базофилы, абс.": (0.0, 20.0),

    "Промиелоциты": (0.0, 100.0),
    "Миелоциты": (0.0, 100.0),
    "Метамиелоциты": (0.0, 100.0),
    "Плазматические клетки": (0.0, 100.0),
    "Активированные лимфоциты": (0.0, 100.0),
    "Атипичные мононуклеары": (0.0, 100.0),
    "Пролимфоциты": (0.0, 100.0),
    "Бласты": (0.0, 100.0),
    "Нормоциты": (0.0, 100.0),
    "СОЭ": (0.0, 120.0),
}


ZERO_WITHOUT_REFERENCE_ALLOWED = {
    "Промиелоциты",
    "Миелоциты",
    "Метамиелоциты",
    "Плазматические клетки",
    "Активированные лимфоциты",
    "Атипичные мононуклеары",
    "Пролимфоциты",
    "Бласты",
    "Нормоциты",
}


def normalize_number_str(value: str) -> str:
    return value.replace(",", ".").strip()


def try_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(normalize_number_str(value))
    except Exception:
        return None


def normalize_indicator_name(indicator: str) -> str:
    indicator = (indicator or "").strip().lower()
    return CBC_CANONICAL_MAP.get(indicator, indicator)


def detect_unit(raw_line: str, canonical_name: str) -> str | None:
    lowered = raw_line.lower()
    expected = EXPECTED_UNITS.get(canonical_name)

    if canonical_name == "Эритроциты":
        return "млн/мкл"
    if canonical_name == "MCV":
        return "фл"
    if canonical_name == "MCH":
        return "пг"
    if canonical_name == "MCHC":
        return "г/дл"
    if canonical_name == "СОЭ":
        return "мм/ч"
    if canonical_name == "Нормоциты":
        return "кл/100 лейк."

    if "кл/100 лейк" in lowered:
        return "кл/100 лейк."
    if "мм/ч" in lowered:
        return "мм/ч"
    if "тыс/мкл" in lowered or "тыс/мк" in lowered or "тыс/мклл" in lowered:
        return "тыс/мкл"
    if "млн/мкл" in lowered or "млн/мк" in lowered:
        return "млн/мкл"
    if "г/дл" in lowered or "гдл" in lowered:
        return "г/дл"
    if "фл" in lowered:
        return "фл"
    if "пг" in lowered:
        return "пг"

    if "%" in raw_line and expected == "%":
        return "%"

    return expected


def extract_all_numbers(raw_line: str) -> list[str]:
    raw_numbers = re.findall(r"\d+[.,]?\d*", raw_line)
    return [normalize_number_str(x) for x in raw_numbers]


def normalize_reference_pair(left: str, right: str, canonical_name: str) -> tuple[str, str]:
    left = normalize_number_str(left)
    right = normalize_number_str(right)

    if canonical_name in {"Лимфоциты, абс.", "Эритроциты"}:
        if re.fullmatch(r"\d{3}", right):
            right = f"{right[0]}.{right[1:]}"

    if canonical_name == "RDW":
        if right in {"48", "48."}:
            right = "14.8"
        if left in {"16", "16."}:
            left = "11.6"

    if canonical_name == "Эритроциты":
        if left == "80":
            left = "3.80"
        if right == "510":
            right = "5.10"

    return left, right


def extract_reference_range_from_line(raw_line: str, canonical_name: str) -> str | None:
    lowered = raw_line.lower()

    if "отсутствуют" in lowered:
        return "отсутствуют"

    match = re.search(r"(\d+[.,]?\d*)\s*-\s*(\d+[.,]?\d*)", raw_line)
    if match:
        left, right = normalize_reference_pair(
            match.group(1),
            match.group(2),
            canonical_name,
        )
        return f"{left} - {right}"

    less_than_match = re.search(r"<\s*(\d+[.,]?\d*)", raw_line)
    if less_than_match:
        return f"< {normalize_number_str(less_than_match.group(1))}"

    numbers = extract_all_numbers(raw_line)
    if len(numbers) >= 3:
        left, right = normalize_reference_pair(numbers[-2], numbers[-1], canonical_name)
        return f"{left} - {right}"

    return None


def is_value_plausible(value: str | None, canonical_name: str) -> bool:
    value_f = try_float(value)
    if value_f is None:
        return False

    low, high = PLAUSIBLE_RANGES.get(canonical_name, (None, None))
    if low is None:
        return True

    return low <= value_f <= high


def pick_value_from_numbers(
    numbers: list[str],
    reference_range: str | None,
    canonical_name: str,
) -> str | None:
    if not numbers:
        return None

    normalized_numbers = [normalize_number_str(x) for x in numbers]

    if reference_range == "отсутствуют":
        first = normalized_numbers[0]
        if is_value_plausible(first, canonical_name):
            return first
        return None

    ref_numbers = []
    if reference_range and reference_range != "отсутствуют":
        ref_numbers = [
            normalize_number_str(x)
            for x in re.findall(r"\d+[.,]?\d*", reference_range)
        ]

    if len(normalized_numbers) >= 3:
        first = normalized_numbers[0]
        if is_value_plausible(first, canonical_name):
            return first

        second = normalized_numbers[1]
        if second not in ref_numbers and is_value_plausible(second, canonical_name):
            return second

        return None

    if len(normalized_numbers) == 2 and ref_numbers:
        if normalized_numbers[0] in ref_numbers and normalized_numbers[1] in ref_numbers:
            return None

    for num in normalized_numbers:
        if num not in ref_numbers and is_value_plausible(num, canonical_name):
            return num

    return None


def determine_status(value: str | None, reference_range: str | None) -> str:
    if value is None:
        return "attention"

    value_f = try_float(value)
    if value_f is None:
        return "attention"

    if reference_range == "отсутствуют":
        if abs(value_f) < 1e-9:
            return "normal"
        return "attention"

    if not reference_range:
        if abs(value_f) < 1e-9:
            return "normal"
        return "attention"

    less_than_match = re.search(r"<\s*(\d+[.,]?\d*)", reference_range)
    if less_than_match:
        limit = try_float(less_than_match.group(1))
        if limit is None:
            return "attention"
        return "normal" if value_f < limit else "high"

    match = re.search(r"(\d+[.,]?\d*)\s*-\s*(\d+[.,]?\d*)", reference_range)
    if not match:
        if abs(value_f) < 1e-9:
            return "normal"
        return "attention"

    low_f = try_float(match.group(1))
    high_f = try_float(match.group(2))

    if low_f is None or high_f is None:
        return "attention"

    if value_f < low_f:
        return "low"
    if value_f > high_f:
        return "high"
    return "normal"


def parse_single_structured_item(item: dict[str, Any]) -> dict[str, Any]:
    indicator = (item.get("indicator") or "").strip().lower()
    raw_line = (item.get("raw_line") or "").strip()
    canonical_name = normalize_indicator_name(indicator)

    numbers_raw = item.get("numbers_found") or []
    numbers = [normalize_number_str(str(x)) for x in numbers_raw if str(x).strip()]

    unit = detect_unit(raw_line, canonical_name)
    reference_range = extract_reference_range_from_line(raw_line, canonical_name)
    value = pick_value_from_numbers(numbers, reference_range, canonical_name)
    status = determine_status(value, reference_range)

    return {
        "name": canonical_name,
        "value": value,
        "unit": unit,
        "reference_range": reference_range,
        "status": status,
        "raw_line": raw_line,
        "numbers_found": numbers,
    }


def deduplicate_parsed_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}

    for item in items:
        name = item.get("name")
        if not name:
            continue

        current_score = 0
        if item.get("value") is not None:
            current_score += 3
        if item.get("unit"):
            current_score += 2
        if item.get("reference_range"):
            current_score += 3
        if item.get("status") and item["status"] != "attention":
            current_score += 1

        old = by_name.get(name)
        if old is None:
            by_name[name] = item
            by_name[name]["_score"] = current_score
            continue

        old_score = old.get("_score", 0)
        if current_score > old_score:
            item["_score"] = current_score
            by_name[name] = item

    result = []
    for value in by_name.values():
        value.pop("_score", None)
        result.append(value)

    ordered_names = list(EXPECTED_UNITS.keys())
    result.sort(
        key=lambda x: ordered_names.index(x["name"]) if x["name"] in ordered_names else 999
    )
    return result


def parse_structured_lab_items(structured_lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parsed = [parse_single_structured_item(item) for item in structured_lines]
    return deduplicate_parsed_items(parsed)


def build_cbc_panel_json(structured_lines: list[dict[str, Any]]) -> dict[str, Any]:
    items = parse_structured_lab_items(structured_lines)

    abnormal = []
    normal = []
    attention = []

    for item in items:
        status = item.get("status")

        if status in {"low", "high"}:
            abnormal.append(item)
        elif status == "normal":
            normal.append(item)
        else:
            attention.append(item)

    return {
        "panel": "CBC",
        "items": items,
        "abnormal_items": abnormal,
        "normal_items": normal,
        "attention_items": attention,
    }


def build_compact_cbc_text(structured_lines: list[dict[str, Any]]) -> str:
    panel = build_cbc_panel_json(structured_lines)
    items = panel.get("items", [])

    if not items:
        return ""

    lines = ["Клинический анализ крови:"]

    for item in items:
        name = item.get("name") or ""
        value = item.get("value")
        unit = item.get("unit") or ""
        ref = item.get("reference_range") or "не удалось определить"
        status = item.get("status") or "attention"

        status_text = {
            "low": "ниже нормы",
            "high": "выше нормы",
            "normal": "в пределах нормы",
            "attention": "требует уточнения",
        }.get(status, "требует уточнения")

        value_text = value if value is not None else "не удалось определить"

        line = f"- {name}: {value_text}"
        if unit and value is not None:
            line += f" {unit}"
        line += f" (реф. {ref}; статус: {status_text})"

        lines.append(line)

    return "\n".join(lines).strip()