# app/services/ai_service.py

# requests — библиотека для HTTP-запросов.
# Она нужна, чтобы отправлять запрос к внешнему AI API (DeepSeek)
# и получать от него ответ.
import requests

# Импортируем настройки проекта:
# - DEEPSEEK_API_KEY — секретный ключ для доступа к API
# - DEEPSEEK_API_URL — адрес, куда отправляется запрос
from app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# Импортируем системный промт и функцию сборки пользовательского промта.
from app.core.prompts import SYSTEM_PROMPT, build_prompt

# Импортируем функцию, которая пытается достать JSON
# из ответа модели.
from app.utils.parsing_utils import extract_json_from_ai_content


def analyze_with_deepseek(
    extracted_text: str,
    user_comment: str = "",
    language: str = "ru",
) -> dict | None:
    """
    Отправляет текст анализа в DeepSeek и пытается получить
    корректный JSON-ответ.

    Возвращает:
    - dict, если модель успешно ответила и JSON удалось извлечь
    - None, если:
      - ключ не задан,
      - запрос завершился ошибкой,
      - модель вернула невалидный JSON,
      - структура ответа оказалась неожиданной
    """

    print("analyze_with_deepseek called")
    print("Has API key:", bool(DEEPSEEK_API_KEY))
    print("Language:", language)
    print("Extracted text length:", len(extracted_text))

    # Если API-ключ пустой, использовать DeepSeek нельзя.
    if not DEEPSEEK_API_KEY.strip():
        print("DeepSeek skipped: API key is empty")
        return None

    # Формируем подробный промт для модели.
    prompt = build_prompt(extracted_text, user_comment, language)

    print("Prompt built successfully")
    print("Prompt length:", len(prompt))

    # Заголовки HTTP-запроса.
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    # Тело запроса к модели.
    #
    # response_format={"type": "json_object"} просит модель
    # вернуть именно JSON-объект.
    #
    # temperature держим низкой, чтобы ответ был стабильнее.
    # max_tokens увеличиваем, чтобы снизить риск обрыва JSON.
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 4000,
        "response_format": {
            "type": "json_object",
        },
    }

    try:
        print("Sending request to DeepSeek...")

        # Отправляем запрос к DeepSeek API.
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        print("DeepSeek status code:", response.status_code)
        print("DeepSeek raw response text (first 1000 chars):")
        print(response.text[:1000])

        # Если сервер вернул ошибку HTTP, поднимется исключение.
        response.raise_for_status()

        # Преобразуем JSON-ответ сервера в словарь Python.
        data = response.json()
        print("DeepSeek HTTP response parsed successfully")

        # Проверяем, что в ответе вообще есть choices.
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            print("DeepSeek response does not contain valid choices")
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            print("DeepSeek first choice has invalid format")
            return None

        # Логируем finish_reason, чтобы понимать,
        # не был ли ответ обрезан по длине.
        finish_reason = first_choice.get("finish_reason")
        print("DeepSeek finish_reason:", finish_reason)

        # Если ответ был обрезан по длине,
        # есть высокий риск неполного JSON.
        if finish_reason == "length":
            print("DeepSeek response was truncated because of token limit")
            return None

        message = first_choice.get("message")
        if not isinstance(message, dict):
            print("DeepSeek message has invalid format")
            return None

        # Достаём основной текст ответа модели.
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            print("DeepSeek content is empty or invalid")
            return None

        print("Model content received (first 1000 chars):")
        print(content[:1000])

        # На всякий случай логируем и конец ответа,
        # чтобы увидеть, не оборвался ли JSON.
        print("Model content tail (last 1000 chars):")
        print(content[-1000:])

        # Пытаемся достать JSON из текста модели.
        parsed = extract_json_from_ai_content(content)

        if parsed is None:
            print("Failed to parse JSON from model content")
            return None

        print("Parsed JSON from model successfully")
        return parsed

    except Exception as e:
        print("DeepSeek request/parsing failed:", repr(e))
        return None