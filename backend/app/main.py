from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Подключаем роуты (маршруты API), которые лежат отдельно.
# Благодаря этому main.py остаётся коротким и чистым.
from app.api.routes import router

# Подключаем название приложения из конфигурации.
from app.core.config import APP_TITLE

# Создаём FastAPI приложение.
# Это главный объект backend-сервиса.
app = FastAPI(title=APP_TITLE)

# Подключаем CORS.
# Это нужно, чтобы frontend (например Flutter, React или другой клиент)
# мог отправлять запросы на backend.
# Сейчас разрешено всё — это удобно для разработки.
# Для production обычно доступ ограничивают конкретными доменами.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все маршруты из файла routes.py.
# После этого endpoint'ы, например /analyze, становятся доступными.
app.include_router(router)