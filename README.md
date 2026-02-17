
AI-doctor

## AI-ВЕТЕРИНАР — Telegram Bot с Web App

Telegram-бот «AI-ВЕТЕРИНАР» с интегрированным Mini App.
Пользователь выбирает специализацию ветеринарного врача и общается с ИИ через чат-интерфейс.

### Технический стек
- Backend: Python 3.10+, aiogram 3.x, FastAPI, uvicorn
- Frontend: HTML, CSS, Vanilla JS (Telegram Web App)
- AI: Pollinations.ai API
- БД: SQLite (aiosqlite)

### Структура проекта
 +├── bot.py # Telegram-бот (aiogram 3) +├── api/ +│ ├── __init__.py +│ └── server.py # FastAPI-сервер (API для Web App) +├── web_app/ +│ ├── index.html # Фронтенд Mini App +│ ├── style.css +│ └── script.js +├── config.py # Конфигурация +├── database.py # Работа с SQLite +├── requirements.txt +└── README.md +

### Установка
bash +pip install -r requirements.txt +

### Настройка
1. Создайте бота через @BotFather
2. Отредактируйте config.py:

BOT_TOKEN — токен бота
WEBAPP_URL — публичный URL вашего Web App (например через ngrok)
POLLINATIONS_API_KEY — ключ Pollinations.ai (опционально)

### Запуск
bash +# Запуск API-сервера и бота одновременно: +python bot.py +

Сервер запустится на порту 8080.
Для продакшена используйте ngrok или разместите на VPS с HTTPS.

bash +ngrok http 8080 +
Полученный HTTPS URL укажите в config.py как WEBAPP_URL.