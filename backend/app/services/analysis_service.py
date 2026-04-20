from app.services.ai_service import analyze_with_deepseek
from app.services.fallback_service import local_medical_analysis, normalize_ai_result
from app.services.validation_service import validate_ai_result_against_extracted_text


def build_text_for_llm(extracted_text: str) -> str:
    """
    Готовим текст для AI:
    - убираем мусор
    - ограничиваем размер
    """

    if not extracted_text:
        return ""

    lines = extracted_text.split("\n")

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # ❌ убираем мусор
        if not line:
            continue
        if len(line) < 3:
            continue
        if any(x in line.lower() for x in ["telegram", "whatsapp", "http"]):
            continue

        cleaned_lines.append(line)

    # 👉 берём только первые 100 строк (хватает с головой)
    cleaned_lines = cleaned_lines[:100]

    return "\n".join(cleaned_lines)


def analyze_text(
    extracted_text: str,
    user_comment: str = "",
    language: str = "ru",
) -> tuple[dict, str]:

    # ✅ готовим текст
    text_for_llm = build_text_for_llm(extracted_text)

    # ❗ fallback если вдруг пусто
    if not text_for_llm:
        text_for_llm = extracted_text[:2000]

    # 🔥 вызываем AI
    ai_result = analyze_with_deepseek(
        extracted_text=text_for_llm,
        user_comment=user_comment,
        language=language,
    )

    # ✅ если AI отработал
    if ai_result is not None:
        print("Using DeepSeek result")

        normalized_result = normalize_ai_result(ai_result)

        validated_result = validate_ai_result_against_extracted_text(
            ai_result=normalized_result,
            extracted_text=extracted_text,
        )

        return validated_result, "deepseek"

    # ❗ fallback
    print("Using local fallback result")

    fallback_result = local_medical_analysis(
        extracted_text=extracted_text,
        user_comment=user_comment,
        language=language,
    )

    return fallback_result, "local_fallback"