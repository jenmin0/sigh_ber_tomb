import sqlite3
import json
import hashlib
import os

DB_PATH = "cybertomb.db"
JSON_PATH = "src/data/burial_data.json"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Create tables with more robust schema and constraints
    c.executescript("""

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
        region_id TEXT,
        display_name TEXT,
        epitaph TEXT,
        avatar_url TEXT,
        guardian_level INTEGER DEFAULT 0,
        lat REAL DEFAULT 0,
        lng REAL DEFAULT 0,
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
                    
    CREATE TABLE IF NOT EXISTS tomb_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposed_by INTEGER REFERENCES users(id),  -- 发起人
        subject_name TEXT NOT NULL,                -- 被立碑者姓名
        subject_bio TEXT,                          -- 简介
        vote_count INTEGER DEFAULT 0,             -- 当前票数
        vote_threshold INTEGER DEFAULT 10,        -- 通过需要的票数
        status TEXT DEFAULT 'voting',             -- voting / approved / rejected
        tomb_id INTEGER REFERENCES tombs(id),     -- 通过后创建的墓碑
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS proposal_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER REFERENCES tomb_proposals(id),
    voter_id INTEGER REFERENCES users(id),
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(proposal_id, voter_id)              -- 每人只能投一票
);
    """)


    # 3. 几个测试用的初始物品
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