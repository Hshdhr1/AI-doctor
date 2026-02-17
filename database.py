new file mode 100644
"""Модуль работы с базой данных SQLite."""

import aiosqlite
import json
from config import DATABASE_PATH


async def init_db():

"""Инициализация базы данных."""
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  await db.execute("""
text
      CREATE TABLE IF NOT EXISTS users (
text
          user_id INTEGER PRIMARY KEY,
text
          language TEXT DEFAULT 'ru',
text
          specialization TEXT DEFAULT 'therapist',
text
          model TEXT DEFAULT 'openai',
text
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
text
      )
text
  """)
text
  await db.execute("""
text
      CREATE TABLE IF NOT EXISTS chat_history (
text
          id INTEGER PRIMARY KEY AUTOINCREMENT,
text
          user_id INTEGER NOT NULL,
text
          role TEXT NOT NULL,
text
          content TEXT NOT NULL,
text
          specialization TEXT NOT NULL,
text
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
text
          FOREIGN KEY (user_id) REFERENCES users(user_id)
text
      )
text
  """)
text
  await db.commit()

async def get_or_create_user(user_id: int) -> dict:

"""Получить или создать пользователя."""
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  db.row_factory = aiosqlite.Row
text
  cursor = await db.execute(
text
      "SELECT * FROM users WHERE user_id = ?", (user_id,)
text
  )
text
  row = await cursor.fetchone()
text
  if row:
text
      return dict(row)
text
  else:
text
      await db.execute(
text
          "INSERT INTO users (user_id) VALUES (?)", (user_id,)
text
      )
text
      await db.commit()
text
      return {
text
          "user_id": user_id,
text
          "language": "ru",
text
          "specialization": "therapist",
text
          "model": "openai",
text
      }

async def update_user_settings(user_id: int, **kwargs):

"""Обновить настройки пользователя."""
allowed_fields = {"language", "specialization", "model"}
fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
if not fields:
text
  return
set_clause = ", ".join(f"{k} = ?" for k in fields)
values = list(fields.values()) + [user_id]
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  await db.execute(
text
      f"UPDATE users SET {set_clause} WHERE user_id = ?", values
text
  )
text
  await db.commit()

async def add_chat_message(user_id: int, role: str, content: str, specialization: str):

"""Добавить сообщение в историю чата."""
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  await db.execute(
text
      "INSERT INTO chat_history (user_id, role, content, specialization) VALUES (?, ?, ?, ?)",
text
      (user_id, role, content, specialization),
text
  )
text
  await db.commit()

async def get_chat_history(user_id: int, specialization: str, limit: int = 20) -> list:

"""Получить историю чата для определённой специализации."""
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  db.row_factory = aiosqlite.Row
text
  cursor = await db.execute(
text
      """SELECT role, content FROM chat_history
text
         WHERE user_id = ? AND specialization = ?
text
         ORDER BY created_at DESC LIMIT ?""",
text
      (user_id, specialization, limit),
text
  )
text
  rows = await cursor.fetchall()
text
  # Возвращаем в хронологическом порядке
text
  return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

async def clear_chat_history(user_id: int, specialization: str = None):

"""Очистить историю чата."""
async with aiosqlite.connect(DATABASE_PATH) as db:
text
  if specialization:
text
      await db.execute(
text
          "DELETE FROM chat_history WHERE user_id = ? AND specialization = ?",
text
          (user_id, specialization),
text
      )
text
  else:
text
      await db.execute(
text
          "DELETE FROM chat_history WHERE user_id = ?", (user_id,)
text
      )
text
  await db.commit()

async def get_user_settings(user_id: int) -> dict:

"""Получить настройки пользователя."""
return await get_or_create_user(user_id)
