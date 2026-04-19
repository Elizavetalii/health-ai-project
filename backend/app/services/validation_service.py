# app/services/validation_service.py

import re


# ============================================================
# КАРТА СИНОНИМОВ ПОКАЗАТЕЛЕЙ
# ============================================================
#
# Здесь мы сопоставляем "нормальное имя" показателя из JSON
# с возможными вариантами, которые могут встретиться в OCR-тексте.
#
# Это нужно, потому что:
# - AI пишет "Гемоглобин"
# - а в OCR может быть "Гемоглобин", "Hemoglobin", "HGB"
# - для нейтрофилов / лейкоцитов / MCHC и т.д. тоже возможны варианты
# ============================================================

INDICATOR_ALIASES = {
    "Гемоглобин": [
        "гемоглобин",
        "hemoglobin",
        "hgb",
    ],
    "Эритроциты": [
        "эритроциты",
        "erythrocytes",
        "rbc",
    ],
    "Лейкоциты": [
        "лейкоциты",
        "лейкюцты",
        "leukocytes",
        "wbc",
    ],
    "Тромбоциты": [
        "тромбоциты",
        "platelets",
        "plt",
    ],
    "MCV": [
        "mcv",
    ],
    "MCH": [
        "mch",
    ],
    "MCHC": [
        "mchc",
    ],
    "RDW": [
        "rdw",
        "row",  # иногда OCR путает RDW -> ROW
    ],
    "Гематокрит": [
        "гематокрит",
        "hematocrit",
        "htc",
        "hct",
        "tak",  # иногда OCR совсем ломает название строки
    ],
    "Нейтрофилы, abs.": [
        "нейтрофилы, abc",
        "нейтрофилы, abs",
        "нейтрофилы abc",
        "нейтрофилы abs",
        "нейтрофилы",
    ],
    "Лимфоциты, abs.": [
        "лимфоциты, abc",
        "лимфоциты, abs",
        "лимфоциты abc",
        "лимфоциты abs",
        "лимфоциты",
    ],
}


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def _normalize_text(text: str) -> str:
    """
    Нормализует текст OCR перед поиском строк.

    Что делаем:
    - приводим к нижнему регистру;
    - выравниваем тире;
    - убираем лишние пробелы.
    """
    text = text.lower()
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _safe_float(value: str) -> float | None:
    """
    Аккуратно превращает строку в число с плавающей точкой.

    Поддерживает:
    - 5.33
    - 5,33
    - 353
    """
    if not value:
        return None

    value = value.replace(",", ".").strip()

    try:
        return float(value)
    except Exception:
        return None


def _extract_numbers_from_line(line: str) -> list[float]:
    """
    Извлекает все числа из строки.

    Это полезно для табличных строк OCR, например:
    'Эритроциты 5.33 млн/мм 3.80 - 5.10'
    """
    raw_numbers = re.findall(r"\d+[.,]?\d*", line)
    numbers = []

    for item in raw_numbers:
        parsed = _safe_float(item)
        if parsed is not None:
            numbers.append(parsed)

    return numbers


def _find_best_line_for_indicator(extracted_text: str, indicator_name: str) -> str | None:
    """
    Ищет наиболее вероятную строку OCR-текста для конкретного показателя.

    Мы не делаем сложный NLP,
    а просто ищем строку по синонимам из INDICATOR_ALIASES.
    """
    normalized_text = _normalize_text(extracted_text)
    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]

    aliases = INDICATOR_ALIASES.get(indicator_name, [indicator_name.lower()])

    for alias in aliases:
        for line in lines:
            if alias in line:
                return line

    return None


def _extract_result_and_reference_from_line(line: str) -> tuple[float | None, float | None, float | None]:
    """
    Пытается вытащить из строки:
    - значение показателя
    - нижнюю границу нормы
    - верхнюю границу нормы

    Это упрощённая эвристика для табличных анализов.

    Ожидаемый паттерн строки:
    'Эритроциты 5.33 ... 3.80 - 5.10'
    """
    numbers = _extract_numbers_from_line(line)

    # Для строки таблицы нам обычно нужно минимум 3 числа:
    # result, ref_min, ref_max
    if len(numbers) < 3:
        return None, None, None

    # Самая частая структура:
    # [result, ref_min, ref_max]
    #
    # Но OCR может вставить лишние числа.
    # Поэтому берём:
    # - первое число как result
    # - два последних числа как референс.
    result_value = numbers[0]
    ref_min = numbers[-2]
    ref_max = numbers[-1]

    # Если референс перевёрнут, попробуем поправить.
    if ref_min > ref_max:
        ref_min, ref_max = ref_max, ref_min

    return result_value, ref_min, ref_max


def _calculate_status(value: float, ref_min: float | None, ref_max: float | None) -> str:
    """
    Вычисляет статус показателя по числу и референсам.
    """
    if ref_min is not None and value < ref_min:
        return "low"

    if ref_max is not None and value > ref_max:
        return "high"

    return "normal"


# ============================================================
# ГЛАВНАЯ ВАЛИДАЦИЯ AI-РЕЗУЛЬТАТА
# ============================================================

def validate_ai_result_against_extracted_text(
    ai_result: dict,
    extracted_text: str,
) -> dict:
    """
    Проверяет результат AI по исходному OCR-тексту.

    Что делает:
    1. Берёт abnormal_values из результата модели.
    2. Для каждого показателя ищет соответствующую строку в OCR.
    3. Пытается достать:
       - значение,
       - ref_min,
       - ref_max.
    4. Если AI-статус явно противоречит референсам,
       исправляет его.
    5. Если показатель оказывается в норме,
       переносит его из abnormal_values в normal_but_relevant_values.

    Важно:
    это консервативная защита.
    Она не "лечит" плохой OCR полностью,
    но помогает не отдавать на экран очевидно неверные статусы.
    """
    if not isinstance(ai_result, dict):
        return ai_result

    abnormal_values = ai_result.get("abnormal_values", [])
    normal_but_relevant_values = ai_result.get("normal_but_relevant_values", [])

    if not isinstance(abnormal_values, list):
        abnormal_values = []

    if not isinstance(normal_but_relevant_values, list):
        normal_but_relevant_values = []

    validated_abnormal_values = []
    added_normal_items = list(normal_but_relevant_values)

    for item in abnormal_values:
        if not isinstance(item, dict):
            continue

        indicator_name = str(item.get("name", "")).strip()
        ai_status = str(item.get("status", "attention")).strip()

        # Если название пустое — просто оставляем как есть.
        if not indicator_name:
            validated_abnormal_values.append(item)
            continue

        best_line = _find_best_line_for_indicator(extracted_text, indicator_name)

        # Если строку не нашли — не трогаем результат AI.
        if not best_line:
            validated_abnormal_values.append(item)
            continue

        value, ref_min, ref_max = _extract_result_and_reference_from_line(best_line)

        # Если не удалось достать числа — не трогаем результат AI.
        if value is None or ref_min is None or ref_max is None:
            validated_abnormal_values.append(item)
            continue

        calculated_status = _calculate_status(value, ref_min, ref_max)

        # ----------------------------------------------------
        # Если по референсам показатель нормальный,
        # а AI назвал его low/high — убираем его из abnormal
        # и переносим в normal_but_relevant_values.
        # ----------------------------------------------------
        if calculated_status == "normal" and ai_status in {"low", "high"}:
            added_normal_items.append(
                {
                    "name": indicator_name,
                    "value": str(value),
                    "comment": (
                        "Автоматическая проверка по извлечённой строке OCR не подтверждает "
                        "явное отклонение. Показатель оставлен как контекстно значимый, "
                        "но без статуса low/high."
                    ),
                }
            )
            continue

        # ----------------------------------------------------
        # Если AI-статус противоречит расчёту, исправляем его.
        # ----------------------------------------------------
        if calculated_status in {"low", "high"} and ai_status != calculated_status:
            corrected_item = dict(item)
            corrected_item["status"] = calculated_status
            corrected_item["value"] = str(value)

            old_comment = str(corrected_item.get("comment", "")).strip()
            corrected_item["comment"] = (
                old_comment
                + " "
                + "Статус скорректирован по автоматически извлечённому референсному диапазону."
            ).strip()

            validated_abnormal_values.append(corrected_item)
            continue

        # Если всё выглядит согласованно — просто обновим value,
        # чтобы на экран ушло число из OCR-строки, а не модельная фантазия.
        corrected_item = dict(item)
        corrected_item["value"] = str(value)
        validated_abnormal_values.append(corrected_item)

    ai_result["abnormal_values"] = validated_abnormal_values
    ai_result["normal_but_relevant_values"] = added_normal_items

    # Можно добавить диагностический комментарий в data_quality.
    analysis_overview = ai_result.get("analysis_overview", {})
    if isinstance(analysis_overview, dict):
        data_quality = analysis_overview.get("data_quality", {})
        if isinstance(data_quality, dict):
            old_comment = str(data_quality.get("comment", "")).strip()
            data_quality["comment"] = (
                old_comment
                + " "
                + "Дополнительно выполнена автоматическая валидация части показателей по OCR-строкам."
            ).strip()
            analysis_overview["data_quality"] = data_quality
            ai_result["analysis_overview"] = analysis_overview

    return ai_result