import json
import re
from typing import Any


def parse_number_from_text(pattern: str, text: str) -> float | None:
    """
    Ищет число в тексте по регулярному выражению.
    """
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None

    raw_value = match.group(1).replace(",", ".").strip()

    try:
        return float(raw_value)
    except ValueError:
        return None


def build_abnormal_item(name: str, value: Any, status: str, comment: str) -> dict:
    """
    Создаёт один объект для abnormal_values.
    """
    return {
        "name": name,
        "value": str(value),
        "status": status,
        "comment": comment,
    }


def extract_json_from_ai_content(content: str) -> dict | None:
    """
    Пытается достать JSON из ответа модели.
    """

    # Шаг 1. Пробуем распарсить как есть.
    try:
        return json.loads(content)
    except Exception:
        pass

    # Шаг 2. Убираем markdown-обёртку.
    cleaned = content.strip()
    cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"^```", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Шаг 3. Пробуем достать первый JSON-объект из текста.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        candidate = match.group(0).strip()
        try:
            return json.loads(candidate)
        except Exception:
            return None

    return None