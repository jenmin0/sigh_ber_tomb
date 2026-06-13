# init_db.py
import sqlite3
import json
import hashlib
import os

DB_PATH = "cybertomb.db"
JSON_PATH = "src/data/burial_data.json"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS regions (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        coordinates_lng REAL,
        coordinates_lat REAL,
        burial_type TEXT NOT NULL,
        description TEXT,
        style_tags TEXT,        -- JSON array存成字符串
        bg_preset TEXT
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        soul_reputation INTEGER DEFAULT 100,
        is_thief INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tombs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        region_id TEXT REFERENCES regions(id),
        display_name TEXT,
        epitaph TEXT,
        avatar_url TEXT,
        guardian_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        rarity INTEGER DEFAULT 1,
        image_url TEXT
    );

    CREATE TABLE IF NOT EXISTS tomb_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tomb_id INTEGER REFERENCES tombs(id),
        item_id INTEGER REFERENCES items(id),
        placed_by INTEGER REFERENCES users(id),
        obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS theft_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thief_id INTEGER REFERENCES users(id),
        target_tomb_id INTEGER REFERENCES tombs(id),
        item_id INTEGER REFERENCES items(id),
        success INTEGER NOT NULL,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 把你们的地图json直接塞进regions表
    if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                regions = json.load(f)

    for r in regions:
        c.execute("""
            INSERT OR REPLACE INTO regions 
            (id, name, coordinates_lng, coordinates_lat, burial_type, description, style_tags, bg_preset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"],
            r["name"],
            r["coordinates"][0],   # lng
            r["coordinates"][1],   # lat
            r["type"],
            r["description"],
            json.dumps(r["styleTags"], ensure_ascii=False),
            r["bgPreset"]
        ))

    # 几个测试用的初始物品
    starter_items = [
        ("赛博莲花", "空灵的数字莲花，来自天葬之地", 2, None),
        ("像素蜡烛", "普通的悼念蜡烛", 1, None),
        ("加密钥匙", "稀有物品，可提升墓碑守护等级", 4, None),
        ("幽灵代码", "神秘的代码碎片", 3, None),
        ("极光碎片", "来自挪威森林的稀有物品", 5, None),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO items (name, description, rarity) VALUES (?, ?, ?)",
        [(i[0], i[1], i[2]) for i in starter_items]
    )

    conn.commit()
    conn.close()
    print("DB initialized.")

if __name__ == "__main__":
    init_db()