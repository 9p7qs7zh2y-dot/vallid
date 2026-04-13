from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime

app = FastAPI(title="Koala Quest API")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.head("/")
async def head_root():
    return {"status": "ok"}

# Модель для сохранения данных (ПОЛНОСТЬЮ СОВПАДАЕТ С ИГРОЙ)
class PlayerSaveData(BaseModel):
    user_id: int
    name: str
    leaves: float
    stars: int
    level: int
    exp: int
    tap_power: float
    energy: int
    max_energy: int
    has_premium: bool
    daily_streak: int
    total_taps: int
    total_leaves: float
    battles_won: int
    boosts: dict
    daily_tasks: dict
    challenges: dict
    last_daily_claim: str = None
    last_energy_update: str = None

# ===== БАЗА ДАННЫХ =====
DB_PATH = "koala_quest.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        leaves REAL DEFAULT 500,
        stars INTEGER DEFAULT 0,
        tap_power REAL DEFAULT 1,
        energy INTEGER DEFAULT 100,
        max_energy INTEGER DEFAULT 100,
        has_premium BOOLEAN DEFAULT 0,
        daily_streak INTEGER DEFAULT 1,
        total_taps INTEGER DEFAULT 0,
        total_leaves REAL DEFAULT 0,
        battles_won INTEGER DEFAULT 0,
        boosts TEXT DEFAULT '{}',
        daily_tasks TEXT DEFAULT '{}',
        challenges TEXT DEFAULT '{}',
        last_daily_claim TEXT,
        last_energy_update TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных SQLite создана")

def get_player(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'user_id': row[0],
        'name': row[1],
        'level': row[2],
        'exp': row[3],
        'leaves': row[4],
        'stars': row[5],
        'tap_power': row[6],
        'energy': row[7],
        'max_energy': row[8],
        'has_premium': bool(row[9]),
        'daily_streak': row[10],
        'total_taps': row[11],
        'total_leaves': row[12],
        'battles_won': row[13],
        'boosts': json.loads(row[14]) if row[14] else {},
        'daily_tasks': json.loads(row[15]) if row[15] else {},
        'challenges': json.loads(row[16]) if row[16] else {},
        'last_daily_claim': row[17],
        'last_energy_update': row[18]
    }

def save_player(player_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO players (
        user_id, name, level, exp, leaves, stars, tap_power,
        energy, max_energy, has_premium, daily_streak, total_taps,
        total_leaves, battles_won, boosts, daily_tasks, challenges, 
        last_daily_claim, last_energy_update
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        player_data['user_id'], player_data['name'], player_data['level'],
        player_data['exp'], player_data['leaves'], player_data['stars'],
        player_data['tap_power'], player_data['energy'], player_data['max_energy'],
        1 if player_data['has_premium'] else 0, player_data['daily_streak'],
        player_data['total_taps'], player_data['total_leaves'], player_data['battles_won'],
        json.dumps(player_data['boosts']), json.dumps(player_data['daily_tasks']),
        json.dumps(player_data['challenges']), 
        player_data.get('last_daily_claim'), player_data.get('last_energy_update')
    ))
    conn.commit()
    conn.close()
    print(f"💾 Сохранён игрок {player_data['user_id']}: {player_data['leaves']}🍃, {player_data['energy']}⚡")

# ========== ЭНДПОИНТЫ ==========
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.post("/api/player/register")
async def register_player(user_id: int, name: str):
    if get_player(user_id):
        return {"status": "exists"}
    new_player = {
        'user_id': user_id,
        'name': name,
        'level': 1,
        'exp': 0,
        'leaves': 500,
        'stars': 0,
        'tap_power': 1,
        'energy': 100,
        'max_energy': 100,
        'has_premium': False,
        'daily_streak': 1,
        'total_taps': 0,
        'total_leaves': 0,
        'battles_won': 0,
        'boosts': {},
        'daily_tasks': {},
        'challenges': {},
        'last_daily_claim': None,
        'last_energy_update': datetime.now().isoformat()
    }
    save_player(new_player)
    return {"status": "success", "player": new_player}

@app.get("/api/player/{user_id}")
async def get_player_data(user_id: int):
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/api/player/save")
async def save_player_data(data: PlayerSaveData):
    player_data = {
        'user_id': data.user_id,
        'name': data.name,
        'level': data.level,
        'exp': data.exp,
        'leaves': data.leaves,
        'stars': data.stars,
        'tap_power': data.tap_power,
        'energy': data.energy,
        'max_energy': data.max_energy,
        'has_premium': data.has_premium,
        'daily_streak': data.daily_streak,
        'total_taps': data.total_taps,
        'total_leaves': data.total_leaves,
        'battles_won': data.battles_won,
        'boosts': data.boosts,
        'daily_tasks': data.daily_tasks,
        'challenges': data.challenges,
        'last_daily_claim': data.last_daily_claim,
        'last_energy_update': data.last_energy_update or datetime.now().isoformat()
    }
    save_player(player_data)
    return {"success": True, "message": "Данные сохранены"}

init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
