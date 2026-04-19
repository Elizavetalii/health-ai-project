# app/services/analysis_service.py

# Импортируем функцию, которая отправляет запрос в AI-модель.
# Она возвращает либо словарь с ответом модели, либо None,
# если AI недоступен или ответ не удалось корректно получить.
from app.services.ai_service import analyze_with_deepseek

# Импортируем:
# - local_medical_analysis: резервный локальный анализ
# - normalize_ai_result: приведение AI-ответа к стабильной структуре
from app.services.fallback_service import local_medical_analysis, normalize_ai_result

# Импортируем слой дополнительной проверки результата AI
# по исходному OCR-тексту.
from app.services.validation_service import validate_ai_result_against_extracted_text


def analyze_text(
    extracted_text: str,
    user_comment: str = "",
    language: str = "ru",
) -> tuple[dict, str]:
    """
    Главная orchestration-функция анализа.

    Логика:
    1. Пытаемся получить результат от DeepSeek.
    2. Если AI ответил — нормализуем его.
    3. Потом дополнительно валидируем часть показателей
       по исходному OCR-тексту.
    4. Если AI не ответил или вернул None — используем локальный fallback.

    Возвращает:
    - итоговый результат анализа
    - источник обработки: deepseek / local_fallback
    """

    ai_result = analyze_with_deepseek(
        extracted_text=extracted_text,
        user_comment=user_comment,
        language=language,
    )

    if ai_result is not None:
        print("Using DeepSeek result")

        normalized_result = normalize_ai_result(ai_result)

        validated_result = validate_ai_result_against_extracted_text(
            ai_result=normalized_result,
            extracted_text=extracted_text,
        )

        return validated_result, "deepseek"

    print("Using local fallback result")

    fallback_result = local_medical_analysis(
        extracted_text=extracted_text,
        user_comment=user_comment,
        language=language,
    )

    return fallback_result, "local_fallback"