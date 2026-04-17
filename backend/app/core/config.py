import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env.
# Это позволяет не хранить секретные ключи прямо в коде.
load_dotenv()

# Ключ для доступа к DeepSeek API.
# Если ключ не найден, вернётся пустая строка.
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# URL API DeepSeek.
# Если в .env он не указан, используем стандартный.
DEEPSEEK_API_URL = os.getenv(
    "DEEPSEEK_API_URL",
    "https://api.deepseek.com/chat/completions",
)

print("DEEPSEEK_API_KEY loaded:", bool(DEEPSEEK_API_KEY))
print("DEEPSEEK_API_URL:", DEEPSEEK_API_URL)

# Список разрешённых форматов файлов.
# Пользователь сможет загружать только такие типы файлов.
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
}

# Название приложения.
# Используется в Swagger / OpenAPI и в заголовке сервиса.
APP_TITLE = "Health AI API"