from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PlayerSaveData(BaseModel):
    user_id: int
    name: str
    leaves: float
    stars: int
    level: int
    exp: int
    tap_power: float
    energy: float
    max_energy: int
    has_premium: bool
    daily_streak: int
    total_taps: int
    total_leaves: float
    battles_won: int
    boosts: dict
    daily_tasks: dict
    challenges: dict
    last_daily_claim: Optional[str] = None
    last_energy_update: Optional[str] = None

def init_db():
    conn = sqlite3.connect('koala_quest.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        leaves REAL,
        stars INTEGER,
        level INTEGER,
        exp INTEGER,
        tap_power REAL,
        energy REAL,
        max_energy INTEGER,
        has_premium INTEGER,
        daily_streak INTEGER,
        total_taps INTEGER,
        total_leaves REAL,
        battles_won INTEGER,
        boosts TEXT,
        daily_tasks TEXT,
        challenges TEXT,
        last_daily_claim TEXT,
        last_energy_update TEXT,
        updated_at TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных готова")

def save_player(data: PlayerSaveData):
    conn = sqlite3.connect('koala_quest.db')
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO players 
    (user_id, name, leaves, stars, level, exp, tap_power, energy, max_energy,
     has_premium, daily_streak, total_taps, total_leaves, battles_won, boosts,
     daily_tasks, challenges, last_daily_claim, last_energy_update, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.user_id, data.name, data.leaves, data.stars, data.level, data.exp,
        data.tap_power, data.energy, data.max_energy, 1 if data.has_premium else 0,
        data.daily_streak, data.total_taps, data.total_leaves, data.battles_won,
        str(data.boosts), str(data.daily_tasks), str(data.challenges),
        data.last_daily_claim, data.last_energy_update, datetime.now()
    ))
    conn.commit()
    conn.close()
    print(f"💾 Игрок {data.user_id} сохранён")

init_db()

# ========== СНАЧАЛА API ЭНДПОИНТЫ ==========
@app.post("/api/player/save")
async def save_player_endpoint(data: PlayerSaveData):
    save_player(data)
    return {"success": True}

@app.get("/api/player/{user_id}")
async def load_player_endpoint(user_id: int):
    conn = sqlite3.connect('koala_quest.db')
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"leaves": 500, "stars": 0, "level": 1, "energy": 100}
    return {
        "user_id": row[0],
        "name": row[1],
        "leaves": row[2],
        "stars": row[3],
        "level": row[4],
        "exp": row[5],
        "tap_power": row[6],
        "energy": row[7],
        "max_energy": row[8],
        "has_premium": bool(row[9]),
        "daily_streak": row[10],
        "total_taps": row[11],
        "total_leaves": row[12],
        "battles_won": row[13],
        "boosts": eval(row[14]) if row[14] else {},
        "daily_tasks": eval(row[15]) if row[15] else {},
        "challenges": eval(row[16]) if row[16] else {}
    }

# ========== ПОТОМ ИГРА (В КОНЦЕ) ==========
@app.get("/")
async def serve_game():
    return FileResponse("index.html")
