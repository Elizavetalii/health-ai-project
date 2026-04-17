# 🧠 Health AI — Анализ медицинских анализов

Health AI — это backend-сервис на FastAPI, который принимает медицинские анализы (PDF, изображения, документы, таблицы), извлекает из них текст и выполняет глубокий предварительный анализ с помощью AI.

Сервис возвращает структурированный JSON с клинической интерпретацией, рисками, возможными состояниями и рекомендациями для дальнейшего обследования.

---

# 🚀 Возможности

✔ Поддержка разных форматов файлов:
- PDF
- JPG / PNG
- DOC / DOCX
- XLS / XLSX
- CSV / TXT

✔ OCR (распознавание текста):
- Поддержка русских и английских анализов
- Предобработка изображений для повышения качества

✔ AI-анализ:
- Подробный разбор анализов
- Выявление отклонений
- Оценка возможных состояний
- Риски и рекомендации
- JSON-структура для фронтенда

✔ Fallback-логика:
- Если AI недоступен → используется локальный анализ

---

# 🏗 Архитектура проекта


app/
│
├── main.py # Точка входа FastAPI
│
├── api/ # API-роуты
│ └── routes.py
│
├── core/ # Базовая логика
│ ├── config.py # Конфигурация (API ключи, URL)
│ └── prompts.py # AI-промты (ОЧЕНЬ ВАЖНЫЙ ФАЙЛ)
│
├── services/ # Бизнес-логика
│ ├── ai_service.py # Работа с DeepSeek API
│ ├── analysis_service.py # Основной анализ (оркестрация)
│ ├── ocr_service.py # Извлечение текста из файлов
│ └── fallback_service.py # Локальный анализ без AI
│
├── models/ # Модели данных
│ └── schemas.py # Pydantic модели ответа
│
├── utils/ # Вспомогательные функции
│ ├── parsing_utils.py # Парсинг JSON от AI
│ └── file_utils.py # Работа с файлами
│
└── init.py # Делает app пакетом Python


---

# 📂 Описание папок и файлов

## 🔹 `main.py`
Точка входа в приложение.

Запускает FastAPI сервер и подключает роуты.

---

## 🔹 `api/routes.py`
Здесь описаны HTTP-эндпоинты.

Основной:
- `POST /analyze` — отправка файла на анализ

---

## 🔹 `core/`

### `config.py`
Содержит:
- API ключи
- URL DeepSeek
- настройки окружения

---

### `prompts.py` ⭐
**Один из самых важных файлов проекта.**

Содержит:
- SYSTEM_PROMPT (поведение AI)
- build_prompt() (формирует запрос к AI)

👉 Именно здесь настраивается:
- глубина анализа
- структура ответа
- логика медицинной интерпретации

---

## 🔹 `services/`

### `ai_service.py`
Отвечает за:
- отправку запроса в DeepSeek
- получение ответа
- извлечение JSON

---

### `analysis_service.py`
Главная логика анализа.

Что делает:
1. Получает текст
2. Вызывает AI
3. Если AI не сработал → fallback
4. Возвращает финальный результат

---

### `ocr_service.py`
Извлекает текст из файлов.

Поддерживает:
- PDF (текст + OCR)
- изображения (OCR)
- DOC / DOCX
- Excel
- CSV / TXT

---

### `fallback_service.py`
Локальный анализ без AI.

Используется если:
- нет API ключа
- ошибка AI

---

## 🔹 `models/schemas.py`
Описание структуры ответа через Pydantic.

👉 Определяет, что именно возвращается фронту.

---

## 🔹 `utils/`

### `parsing_utils.py`
Извлекает JSON из ответа AI.

Потому что AI может вернуть:
- JSON
- JSON в тексте
- JSON с мусором

---

### `file_utils.py`
Работа с файлами:
- декодирование
- обработка CSV
- работа с байтами

---

# ⚙️ Установка и запуск

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
2. Настройка .env

Создай файл .env:

DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
3. Установка системных зависимостей
macOS
brew install tesseract
brew install poppler
brew install libreoffice
Windows

Установить:

Tesseract OCR
Poppler
LibreOffice

И добавить их в PATH.

4. Запуск сервера
uvicorn app.main:app --reload
📡 API
POST /analyze
Запрос:
file (файл анализа)
language (ru/en)
user_comment (опционально)
Ответ:
{
  "success": true,
  "analysis_result": {
    "summary": "...",
    "abnormal_values": [],
    "possible_conditions": [],
    "recommendations": []
  }
}