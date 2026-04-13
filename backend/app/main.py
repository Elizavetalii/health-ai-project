import json
import os
import re
import tempfile
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from PIL import Image
import pytesseract

load_dotenv()

app = FastAPI(title="Health AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image, lang="rus+eng")
    return text.strip()


def extract_text_from_file(file_path: str, file_extension: str) -> str:
    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if file_extension in {".jpg", ".jpeg", ".png"}:
        return extract_text_from_image(file_path)

    return ""


def build_prompt(extracted_text: str, user_comment: str = "", language: str = "ru") -> str:
    comment_block = ""
    if user_comment.strip():
        if language == "ru":
            comment_block = f"\nДополнительный комментарий пользователя:\n{user_comment.strip()}\n"
        else:
            comment_block = f"\nAdditional user comment:\n{user_comment.strip()}\n"

    if language == "ru":
        return f"""
Ты медицинский AI-ассистент для предварительного анализа лабораторных результатов.

Важно:
- Не ставь диагноз.
- Не утверждай ничего категорично.
- Не назначай лечение.
- Не пиши, что пользователь точно болен.
- Не указывай конкретные препараты как назначение лечения.
- Вместо этого можно писать, какие варианты можно обсудить с врачом.
- Укажи, что нужна очная консультация врача.
- Ответ верни строго в JSON без markdown и без пояснений вне JSON.

Нужный формат:
{{
  "summary": "краткое понятное резюме",
  "abnormal_values": [
    {{
      "name": "название показателя",
      "value": "значение",
      "status": "low/high/attention",
      "comment": "краткий комментарий"
    }}
  ],
  "risks": ["возможные риски или на что обратить внимание"],
  "recommended_doctors": ["к каким врачам можно обратиться"],
  "possible_support_options": ["какие меры или направления можно обсудить с врачом"],
  "recommendations": ["какие шаги можно обсудить с врачом"],
  "disclaimer": "это не диагноз..."
}}

{comment_block}
Вот текст анализа:
{extracted_text}
"""
    else:
        return f"""
You are a medical AI assistant for preliminary interpretation of laboratory test results.

Important:
- Do not make a diagnosis.
- Do not make categorical claims.
- Do not prescribe treatment.
- Do not say that the user definitely has a disease.
- Do not name specific medications as treatment prescriptions.
- You may mention options that can be discussed with a doctor.
- Say that an in-person doctor consultation is required.
- Return the answer strictly in JSON, without markdown and without any text outside JSON.

Required format:
{{
  "summary": "short plain summary",
  "abnormal_values": [
    {{
      "name": "indicator name",
      "value": "value",
      "status": "low/high/attention",
      "comment": "short comment"
    }}
  ],
  "risks": ["possible risks or things to pay attention to"],
  "recommended_doctors": ["which doctors may be relevant"],
  "possible_support_options": ["what support options may be discussed with a doctor"],
  "recommendations": ["what next steps can be discussed with a doctor"],
  "disclaimer": "this is not a diagnosis..."
}}

{comment_block}
Laboratory analysis text:
{extracted_text}
"""


def parse_number_from_text(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None

    raw_value = match.group(1).replace(",", ".").strip()

    try:
        return float(raw_value)
    except ValueError:
        return None


def build_abnormal_item(name: str, value: Any, status: str, comment: str) -> dict:
    return {
        "name": name,
        "value": str(value),
        "status": status,
        "comment": comment,
    }


def normalize_ai_result(result: dict) -> dict:
    if not isinstance(result, dict):
        return fallback_empty_result("Не удалось корректно получить ответ модели")

    return {
        "summary": str(result.get("summary", "Нет данных")),
        "abnormal_values": result.get("abnormal_values", []),
        "risks": result.get("risks", []),
        "recommended_doctors": result.get("recommended_doctors", []),
        "possible_support_options": result.get("possible_support_options", []),
        "recommendations": result.get("recommendations", []),
        "disclaimer": str(
            result.get(
                "disclaimer",
                "Это не диагноз. Для точной интерпретации нужна консультация врача.",
            )
        ),
    }


def fallback_empty_result(summary: str) -> dict:
    return {
        "summary": summary,
        "abnormal_values": [],
        "risks": [],
        "recommended_doctors": [],
        "possible_support_options": [],
        "recommendations": [],
        "disclaimer": "Это не диагноз. Для точной интерпретации нужна консультация врача.",
    }


def local_medical_analysis(extracted_text: str, user_comment: str = "", language: str = "ru") -> dict:
    abnormal_values = []
    risks = []
    recommended_doctors = set()
    possible_support_options = set()
    recommendations = set()

    hemoglobin = parse_number_from_text(
        r"(?:гемоглобин|hemoglobin|hgb)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )
    glucose = parse_number_from_text(
        r"(?:глюкоза|glucose)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )
    cholesterol = parse_number_from_text(
        r"(?:холестерин|cholesterol)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )
    leukocytes = parse_number_from_text(
        r"(?:лейкоциты|leukocytes|wbc)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )
    platelets = parse_number_from_text(
        r"(?:тромбоциты|platelets|plt)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    if hemoglobin is not None:
        if hemoglobin < 120:
            abnormal_values.append(
                build_abnormal_item(
                    "Гемоглобин",
                    hemoglobin,
                    "low",
                    "Показатель может быть снижен.",
                )
            )
            risks.append("Стоит исключить анемию или дефицитные состояния.")
            recommended_doctors.update(["Терапевт", "Гематолог"])
            possible_support_options.update([
                "С врачом можно обсудить обследование на дефицит железа и ферритина.",
            ])
            recommendations.update([
                "Обсудить с врачом необходимость повторного общего анализа крови.",
                "При необходимости проверить железо, ферритин, витамин B12.",
            ])
        elif hemoglobin > 160:
            abnormal_values.append(
                build_abnormal_item(
                    "Гемоглобин",
                    hemoglobin,
                    "high",
                    "Показатель может быть повышен.",
                )
            )
            risks.append("Повышение гемоглобина требует очной оценки с учётом симптомов.")
            recommended_doctors.update(["Терапевт"])
            recommendations.add("Обсудить результат с врачом и при необходимости пересдать анализ.")

    if glucose is not None and glucose > 6.1:
        abnormal_values.append(
            build_abnormal_item(
                "Глюкоза",
                glucose,
                "high",
                "Показатель может быть выше референсных значений.",
            )
        )
        risks.append("Стоит исключить нарушение углеводного обмена.")
        recommended_doctors.update(["Терапевт", "Эндокринолог"])
        possible_support_options.update([
            "С врачом можно обсудить повторную проверку глюкозы или HbA1c.",
        ])
        recommendations.update([
            "Уточнить, сдавался ли анализ натощак.",
            "Обсудить с врачом необходимость дополнительного обследования.",
        ])

    if cholesterol is not None and cholesterol > 5.2:
        abnormal_values.append(
            build_abnormal_item(
                "Холестерин",
                cholesterol,
                "high",
                "Показатель может быть повышен.",
            )
        )
        risks.append("Повышенный холестерин может быть фактором сердечно-сосудистого риска.")
        recommended_doctors.update(["Терапевт", "Кардиолог"])
        possible_support_options.add(
            "С врачом можно обсудить липидный профиль и коррекцию образа жизни."
        )
        recommendations.update([
            "Обсудить питание, физическую активность и семейный анамнез.",
            "При необходимости сдать расширенный липидный профиль.",
        ])

    if leukocytes is not None:
        if leukocytes > 9.0:
            abnormal_values.append(
                build_abnormal_item(
                    "Лейкоциты",
                    leukocytes,
                    "high",
                    "Показатель может быть повышен.",
                )
            )
            risks.append("Повышение лейкоцитов может встречаться при воспалении или инфекции.")
            recommended_doctors.update(["Терапевт"])
            recommendations.add("Сопоставить результат с жалобами и другими показателями крови.")
        elif leukocytes < 4.0:
            abnormal_values.append(
                build_abnormal_item(
                    "Лейкоциты",
                    leukocytes,
                    "low",
                    "Показатель может быть снижен.",
                )
            )
            risks.append("Снижение лейкоцитов требует оценки врачом.")
            recommended_doctors.update(["Терапевт", "Гематолог"])
            recommendations.add("При необходимости повторить общий анализ крови.")

    if platelets is not None:
        if platelets < 150:
            abnormal_values.append(
                build_abnormal_item(
                    "Тромбоциты",
                    platelets,
                    "low",
                    "Показатель может быть снижен.",
                )
            )
            risks.append("Снижение тромбоцитов требует дополнительной оценки.")
            recommended_doctors.update(["Терапевт", "Гематолог"])
            recommendations.add("Обсудить результат с врачом и необходимость повторного анализа.")
        elif platelets > 400:
            abnormal_values.append(
                build_abnormal_item(
                    "Тромбоциты",
                    platelets,
                    "high",
                    "Показатель может быть повышен.",
                )
            )
            risks.append("Повышение тромбоцитов требует интерпретации с учётом клинической картины.")
            recommended_doctors.update(["Терапевт"])
            recommendations.add("Повторить анализ по рекомендации врача.")

    if user_comment.strip():
        lowered_comment = user_comment.lower()
        if any(word in lowered_comment for word in ["слабость", "усталость", "головокруж", "weakness", "fatigue"]):
            risks.append("Жалобы пользователя стоит учитывать при интерпретации результатов.")
            recommendations.add("Сообщить врачу о симптомах и времени их появления.")

    if not abnormal_values:
        summary = (
            "Явных отклонений по автоматически распознанным показателям не найдено, "
            "но результат всё равно стоит показать врачу."
        )
        risks.append("Локальный автоматический анализ ограничен и не заменяет медицинскую интерпретацию.")
        recommended_doctors.add("Терапевт")
        recommendations.update([
            "Показать результат врачу.",
            "Сопоставить показатели с жалобами и анамнезом.",
        ])
    else:
        summary = "Обнаружены показатели, которые могут требовать дополнительного внимания и очной оценки врачом."

    if not possible_support_options:
        possible_support_options.add("Все дальнейшие шаги и варианты поддержки следует обсуждать с врачом.")

    return {
        "summary": summary,
        "abnormal_values": abnormal_values,
        "risks": list(risks),
        "recommended_doctors": list(recommended_doctors),
        "possible_support_options": list(possible_support_options),
        "recommendations": list(recommendations),
        "disclaimer": "Это не диагноз и не назначение лечения. Для точной интерпретации анализа нужна очная консультация врача.",
    }


def analyze_with_deepseek(extracted_text: str, user_comment: str = "", language: str = "ru") -> dict:
    if not DEEPSEEK_API_KEY.strip():
        return local_medical_analysis(extracted_text, user_comment, language)

    prompt = build_prompt(extracted_text, user_comment, language)

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are a careful medical analysis assistant. Always return valid JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(content)
            return normalize_ai_result(parsed)
        except json.JSONDecodeError:
            return local_medical_analysis(extracted_text, user_comment, language)

    except Exception:
        return local_medical_analysis(extracted_text, user_comment, language)


@app.get("/")
def root():
    return {"message": "Backend is working"}


@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    language: str = Form("ru"),
    user_comment: str = Form(""),
):
    if not file.filename:
        return {
            "success": False,
            "message": "Файл не выбран",
        }

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "filename": file.filename,
            "language": language,
            "message": "Поддерживаются только PDF, JPG, JPEG и PNG",
        }

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        extracted_text = extract_text_from_file(temp_file_path, file_extension)

        if not extracted_text:
            return {
                "success": False,
                "filename": file.filename,
                "language": language,
                "message": "Не удалось извлечь текст из файла",
            }

        ai_result = analyze_with_deepseek(
            extracted_text=extracted_text,
            user_comment=user_comment,
            language=language,
        )

        return {
            "success": True,
            "filename": file.filename,
            "language": language,
            "message": "Анализ успешно обработан",
            "analysis_result": ai_result,
            "meta": {
                "source_type": "deepseek" if DEEPSEEK_API_KEY.strip() else "local_fallback",
                "user_comment_used": bool(user_comment.strip()),
                "file_type": file_extension.replace(".", ""),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "filename": file.filename,
            "language": language,
            "message": f"Ошибка при обработке файла: {str(e)}",
        }

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)