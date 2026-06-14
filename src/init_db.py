import sqlite3
import json
import hashlib
import os
from seed_demo_tombs import seed
DB_PATH = "cybertomb.db"
JSON_PATH = "src/data/burial_data.json"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Create tables with more robust schema and constraints
    c.executescript("""

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        shape TEXT DEFAULT 'arch',
        color TEXT DEFAULT '#c9a874'
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
        proposed_by INTEGER REFERENCES users(id),  -- ID of the user who proposed
        subject_name TEXT NOT NULL,                -- Name of the person to be memorialized
        subject_bio TEXT,                          -- Biography
        vote_count INTEGER DEFAULT 0,             -- Current vote count
        vote_threshold INTEGER DEFAULT 10,        -- Votes required for approval
        status TEXT DEFAULT 'voting',             -- voting / approved / rejected
        tomb_id INTEGER REFERENCES tombs(id),     -- Tomb created after approval
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS proposal_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER REFERENCES tomb_proposals(id),
    voter_id INTEGER REFERENCES users(id),
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(proposal_id, voter_id)              -- Each user can only vote once
);
    """)


    # 3. Initialize items from JSON
    starter_items = [
        ("cyber lotus", "Ethereal digital lotus, from the realm of digital burial", 2, None),
        ("pixel candle", "Ordinary memorial candle", 1, None),
        ("encryption key", "Rare item that can enhance tomb guardian level", 4, None),
        ("ghost code", "Mysterious code fragment", 3, None),
        ("aurora fragment", "Rare item from the Norwegian forests", 5, None),

    ]
    c.executemany(
        "INSERT OR IGNORE INTO items (name, description, rarity) VALUES (?, ?, ?)",
        [(i[0], i[1], i[2]) for i in starter_items]
    )

    conn.commit()
    conn.close()
    print("DB initialized.")
    seed()

if __name__ == "__main__":
    init_db()
