# db.py
import sqlite3
import json
import random
import hashlib

DB_PATH = "cybertomb.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Let results be accessed as a dictionary
    return conn

def get_all_regions():
    """Initial page load: get all regions to render the map"""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM regions").fetchall()
        return [dict(r) for r in rows]


def get_tomb_items(tomb_id: int):
    """Initial page load: get all items for a specific tomb to render the tomb space"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT i.*, ti.placed_by, ti.obtained_at
            FROM tomb_items ti
            JOIN items i ON ti.item_id = i.id
            WHERE ti.tomb_id = ?
        """, (tomb_id,)).fetchall()
        return [dict(r) for r in rows]
    

def get_tombs_by_region(region_id: str):
    """Initial page load: get all tombs for a specific region to render the map markers"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT t.*, u.email  
            FROM tombs t 
            JOIN users u ON t.user_id = u.id
            WHERE t.region_id = ?
        """, (region_id,)).fetchall()
        return [dict(r) for r in rows]

def create_user_with_tomb(email: str, password: str, region_id: str, display_name: str, epitaph: str, lat: float = 0.0, lng: float = 0.0):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_conn() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash)
            )
            user_id = cursor.lastrowid
            
            cursor2 = conn.execute(
                "INSERT INTO tombs (user_id, region_id, display_name, epitaph, lat, lng) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, region_id, display_name, epitaph, lat, lng)
            )
            tomb_id = cursor2.lastrowid
            conn.commit()
            
            return {
                "id": tomb_id,          
                "user_id": user_id,     
                "tomb_id": tomb_id,     
                "display_name": display_name,
                "tomb": {
                    "id": tomb_id,
                    "display_name": display_name,
                    "region_id": region_id,
                    "epitaph": epitaph,
                    "lat": lat,
                    "lng": lng,
                    "shape": "arch",   
                    "color": "#c9a874"
                }
            }
        except sqlite3.IntegrityError:
            return None

def attempt_steal(thief_id: int, target_tomb_id: int, item_id: int):
    """
    Steal attempt logic:
    The success rate is determined by three factors:
    1. Item rarity (1-5): higher rarity is harder to steal
    2. Guardian level of the target tomb (0-10): higher level means stronger defenses
    3. Reputation of the thief (0-200): higher reputation means better luck
    Base success rate is 50%, then modified by:
    - Rarity penalty: each rarity level above 1 reduces success by 8%
    - Guardian penalty: each guardian level reduces success by 4%
    - Reputation bonus: each point of reputation above 100 adds 0.1% success, below 100 subtracts 0.1%
    """
    with get_conn() as conn:

        # 1. Check if the item exists in the target tomb and get its rarity
        item = conn.execute("""
            SELECT i.rarity FROM tomb_items ti
            JOIN items i ON ti.item_id = i.id
            WHERE ti.tomb_id = ? AND ti.item_id = ?
        """, (target_tomb_id, item_id)).fetchone()

        if not item:
            return {"error": "Item not found in target tomb"}

        # 2. Get the guardian level and thief's reputation
        tomb = conn.execute(
            "SELECT guardian_level FROM tombs WHERE id = ?",
            (target_tomb_id,)
        ).fetchone()

        thief = conn.execute(
            "SELECT soul_reputation, is_thief FROM users WHERE id = ?",
            (thief_id,)
        ).fetchone()

        rarity = item["rarity"]               # 1-5
        guardian = tomb["guardian_level"]     # 0-10
        reputation = thief["soul_reputation"] # 0-200, init 100

        # 3. Compute success rate
        # Base success rate is 50%, rarity and guardian level reduce it, reputation increases it
        base = 0.5
        rarity_penalty   = (rarity - 1) * 0.08    # max -0.32
        guardian_penalty = guardian * 0.04         # each -4%
        rep_bonus = (reputation - 100) * 0.001     # reputation bonus: above 100 adds 0.1%, below 100 subtracts 0.1%

        success_rate = base - rarity_penalty - guardian_penalty + rep_bonus
        success_rate = max(0.05, min(0.85, success_rate))  # limit to 5%-85%

        success = random.random() < success_rate

        # 4. log the attempt
        conn.execute("""
            INSERT INTO theft_logs (thief_id, target_tomb_id, item_id, success)
            VALUES (?, ?, ?, ?)
        """, (thief_id, target_tomb_id, item_id, int(success)))

        if success:
            # transfer the item to the thief's tomb
            thief_tomb = conn.execute(
                "SELECT id FROM tombs WHERE user_id = ?", (thief_id,)
            ).fetchone()

            conn.execute("""
                UPDATE tomb_items SET tomb_id = ?, placed_by = ?
                WHERE tomb_id = ? AND item_id = ?
            """, (thief_tomb["id"], thief_id, target_tomb_id, item_id))

            # reputation slightly decreases
            conn.execute(
                "UPDATE users SET soul_reputation = MAX(0, soul_reputation - 5) WHERE id = ?",
                (thief_id,)
            )

            conn.commit()
            return {
                "success": True,
                "message": "Steal successful! The item has been moved to your tomb.",
                "success_rate": round(success_rate, 2)
            }

        else:
            # Punishment for failed steal attempt
            penalty = _apply_theft_penalty(conn, thief_id, rarity)
            conn.commit()
            return {
                "success": False,
                "message": "Steal failed",
                "penalty": penalty,
                "success_rate": round(success_rate, 2)
            }


def _apply_theft_penalty(conn, thief_id: int, rarity: int):
    """
    Punishment for failed steal attempt, the rarer the item, the heavier the penalty
    rarity 1-2: Only reputation decreases
    rarity 3:   Mark as thief + reputation decreases
    rarity 4-5: Mark as thief + significant reputation decrease + random item lost from own tomb
    """
    rep_loss = rarity * 8  # 8 / 16 / 24 / 32 / 40

    conn.execute(
        "UPDATE users SET soul_reputation = MAX(0, soul_reputation - ?) WHERE id = ?",
        (rep_loss, thief_id)
    )

    if rarity >= 3:
        conn.execute(
            "UPDATE users SET is_thief = 1 WHERE id = ?",
            (thief_id,)
        )

    lost_item = None
    if rarity >= 4:
        # Take a random item from the thief's own tomb as additional punishment
        thief_tomb = conn.execute(
            "SELECT id FROM tombs WHERE user_id = ?", (thief_id,)
        ).fetchone()

        if thief_tomb:
            victim_item = conn.execute("""
                SELECT ti.id, i.name FROM tomb_items ti
                JOIN items i ON ti.item_id = i.id
                WHERE ti.tomb_id = ?
                ORDER BY RANDOM() LIMIT 1
            """, (thief_tomb["id"],)).fetchone()

            if victim_item:
                conn.execute(
                    "DELETE FROM tomb_items WHERE id = ?",
                    (victim_item["id"],)
                )
                lost_item = victim_item["name"]

    penalty_desc = f"reputation -{rep_loss}"
    if rarity >= 3:
        penalty_desc += " · Marked as thief"
    if lost_item:
        penalty_desc += f" · Your '{lost_item}' was taken back by the ghost"

    return penalty_desc