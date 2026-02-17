new file mode 100644
"""FastAPI-сервер для обработки запросов от Web App."""

import logging
import aiohttp
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from config import (

POLLINATIONS_API_URL,
POLLINATIONS_API_KEY,
SPECIALIZATIONS,
AVAILABLE_MODELS,

)
from database import (

init_db,
get_or_create_user,
update_user_settings,
add_chat_message,
get_chat_history,
clear_chat_history,
get_user_settings,

)

logger = logging.getLogger(name)

app = FastAPI(title="AI-ВЕТЕРИНАР API")

# CORS для Web App
app.add_middleware(

CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],

)


# ---- Pydantic-модели ----

class ChatRequest(BaseModel):

user_id: int
message: str
specialization: Optional[str] = None
language: Optional[str] = None
model: Optional[str] = None

class SettingsRequest(BaseModel):

user_id: int
language: Optional[str] = None
specialization: Optional[str] = None
model: Optional[str] = None

class ClearHistoryRequest(BaseModel):

user_id: int
specialization: Optional[str] = None

# ---- Эндпоинты ----

@app.on_event("startup")
async def startup():

await init_db()

@app.get("/api/specializations")
async def get_specializations(lang: str = "ru"):

"""Получить список специализаций."""
result = []
for key, spec in SPECIALIZATIONS.items():
text
  result.append({
text
      "id": key,
text
      "icon": spec["icon"],
text
      "name": spec["name"].get(lang, spec["name"]["en"]),
text
  })
return {"specializations": result}

@app.get("/api/models")
async def get_models():

"""Получить список доступных моделей."""
return {"models": AVAILABLE_MODELS}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):

"""Получить настройки пользователя."""
user = await get_or_create_user(user_id)
return {"user": user}

@app.post("/api/settings")
async def save_settings(req: SettingsRequest):

"""Сохранить настройки пользователя."""
await get_or_create_user(req.user_id)
update_data = {}
if req.language:
text
  update_data["language"] = req.language
if req.specialization:
text
  update_data["specialization"] = req.specialization
if req.model:
text
  update_data["model"] = req.model
if update_data:
text
  await update_user_settings(req.user_id, **update_data)
user = await get_user_settings(req.user_id)
return {"status": "ok", "user": user}

@app.post("/api/chat")
async def chat(req: ChatRequest):

"""Отправить сообщение AI-ветеринару."""
try:
text
  # Получить / создать пользователя
text
  user = await get_or_create_user(req.user_id)
text
  # Определить параметры
text
  spec_key = req.specialization or user.get("specialization", "therapist")
text
  lang = req.language or user.get("language", "ru")
text
  model = req.model or user.get("model", "openai")
text
  # Обновить настройки если переданы
text
  updates = {}
text
  if req.specialization:
text
      updates["specialization"] = req.specialization
text
  if req.language:
text
      updates["language"] = req.language
text
  if req.model:
text
      updates["model"] = req.model
text
  if updates:
text
      await update_user_settings(req.user_id, **updates)
text
  # Системный промпт
text
  spec = SPECIALIZATIONS.get(spec_key, SPECIALIZATIONS["therapist"])
text
  system_prompt = spec["system_prompt"].get(lang, spec["system_prompt"]["en"])
text
  # Сохранить сообщение пользователя
text
  await add_chat_message(req.user_id, "user", req.message, spec_key)
text
  # Получить историю
text
  history = await get_chat_history(req.user_id, spec_key, limit=20)
text
  # Сформировать массив messages
text
  messages = [{"role": "system", "content": system_prompt}]
text
  messages.extend(history)
text
  # Вызов Pollinations.ai
text
  payload = {
text
      "model": model,
text
      "messages": messages,
text
      "stream": False,
text
      "temperature": 0.7,
text
  }
text
  headers = {"Content-Type": "application/json"}
text
  if POLLINATIONS_API_KEY:
text
      headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"
text
  async with aiohttp.ClientSession() as session:
text
      async with session.post(
text
          POLLINATIONS_API_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
text
      ) as resp:
text
          if resp.status != 200:
text
              error_text = await resp.text()
text
              logger.error(f"Pollinations API error {resp.status}: {error_text}")
text
              return JSONResponse(
text
                  status_code=502,
text
                  content={
text
                      "error": True,
text
                      "message": "AI service is temporarily unavailable. Please try again later."
text
                      if lang == "en"
text
                      else "Сервис ИИ временно недоступен. Попробуйте позже.",
text
                  },
text
              )
text
          data = await resp.json()
text
  # Извлечь ответ
text
  ai_message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
text
  if not ai_message:
text
      ai_message = "Sorry, I couldn't generate a response." if lang == "en" else "Извините, не удалось сгенерировать ответ."
text
  # Сохранить ответ в историю
text
  await add_chat_message(req.user_id, "assistant", ai_message, spec_key)
text
  return {
text
      "response": ai_message,
text
      "specialization": spec_key,
text
      "model": model,
text
  }
except aiohttp.ClientError as e:
text
  logger.error(f"Network error: {e}")
text
  return JSONResponse(
text
      status_code=502,
text
      content={"error": True, "message": "Network error. Please try again."},
text
  )
except Exception as e:
text
  logger.error(f"Unexpected error: {e}", exc_info=True)
text
  return JSONResponse(
text
      status_code=500,
text
      content={"error": True, "message": "Internal server error."},
text
  )

@app.post("/api/clear_history")
async def clear_history(req: ClearHistoryRequest):

"""Очистить историю чата."""
await clear_chat_history(req.user_id, req.specialization)
return {"status": "ok"}

@app.get("/api/history/{user_id}/{specialization}")
async def get_history(user_id: int, specialization: str):

"""Получить историю чата."""
history = await get_chat_history(user_id, specialization, limit=50)
return {"history": history}

# Статические файлы Web App — монтируются последними
app.mount("/", StaticFiles(directory="web_app", html=True), name="webapp")