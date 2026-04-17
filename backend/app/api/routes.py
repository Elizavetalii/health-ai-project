import os
import tempfile

from fastapi import APIRouter, File, Form, UploadFile

# Импортируем разрешённые форматы файлов.
from app.core.config import ALLOWED_EXTENSIONS

# Импортируем функцию анализа текста.
from app.services.analysis_service import analyze_text

# Импортируем функцию извлечения текста из файла.
from app.services.ocr_service import extract_text_from_file

# Создаём router.
# Он нужен, чтобы хранить endpoint'ы отдельно от main.py.
router = APIRouter()


@router.get("/")
def root():
    """
    Простой тестовый endpoint.
    Если открыть /, можно понять, что backend вообще работает.
    """
    return {"message": "Backend is working"}


@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    language: str = Form("ru"),
    user_comment: str = Form(""),
):
    """
    Главный endpoint анализа файла.

    Что получает:
    - file: файл анализа
    - language: язык ответа (по умолчанию русский)
    - user_comment: комментарий пользователя

    Что делает:
    1. Проверяет файл
    2. Сохраняет его временно
    3. Извлекает текст
    4. Отправляет текст в анализ
    5. Возвращает JSON с результатом
    """

    # Если имя файла отсутствует — значит файл не был выбран.
    if not file.filename:
        return {
            "success": False,
            "message": "Файл не выбран",
        }

    # Получаем расширение файла, например .pdf
    file_extension = os.path.splitext(file.filename)[1].lower()

    # Проверяем, входит ли расширение в список допустимых.
    if file_extension not in ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "filename": file.filename,
            "language": language,
            "message": "Поддерживаются: PDF, JPG, JPEG, PNG, DOC, DOCX, XLS, XLSX, CSV, TXT",
        }

    # Создаём временный файл и записываем туда содержимое загруженного файла.
    # Это нужно, потому что дальше удобнее работать с обычным путём к файлу.
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        # Пытаемся извлечь текст из файла.
        extracted_text = extract_text_from_file(temp_file_path, file_extension)

        # Если текст пустой, значит распознать файл не удалось.
        if not extracted_text.strip():
            return {
                "success": False,
                "filename": file.filename,
                "language": language,
                "message": "Не удалось извлечь текст из файла",
            }

        # Передаём извлечённый текст в сервис анализа.
        analysis_result = analyze_text(
            extracted_text=extracted_text,
            user_comment=user_comment,
            language=language,
        )

        # Успешный ответ.
        return {
            "success": True,
            "filename": file.filename,
            "language": language,
            "message": "Анализ успешно обработан",
            "analysis_result": analysis_result,
            "meta": {
                "user_comment_used": bool(user_comment.strip()),
                "file_type": file_extension.replace(".", ""),
                "extracted_text_length": len(extracted_text),
            },
        }

    except Exception as e:
        # Если что-то пошло не так — возвращаем ошибку.
        return {
            "success": False,
            "filename": file.filename,
            "language": language,
            "message": f"Ошибка при обработке файла: {str(e)}",
        }

    finally:
        # В любом случае удаляем временный файл,
        # чтобы не засорять систему.
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)