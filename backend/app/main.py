# ============================================================
# Точка входа backend-сервиса Health AI
# ============================================================

# FastAPI — основной фреймворк сервиса.
from fastapi import FastAPI

# CORSMiddleware — механизм, позволяющий frontend-приложениям безопасно взаимодействовать с API.
from fastapi.middleware.cors import CORSMiddleware

# Подключение API-роутов
from app.api.routes import router

# Конфигурация приложения
from app.core.config import APP_TITLE


# Инициализация FastAPI приложения
app = FastAPI(title=APP_TITLE)


# ------------------------------------------------------------
# CORS настройка (разрешает frontend обращаться к backend)
# В production желательно ограничить allow_origins
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение всех API маршрутов (например /analyze)
app.include_router(router)


# Простой endpoint для проверки работы сервиса (health check)
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Health AI Backend",
    }