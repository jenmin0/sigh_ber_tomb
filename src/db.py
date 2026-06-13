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
    """朋友地图初始化时调用，拿所有地区"""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM regions").fetchall()
        return [dict(r) for r in rows]

def get_tombs_by_region(region_id: str):
    """点击地图某个地区时，拿该地区所有墓碑"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT t.*, u.username 
            FROM tombs t 
            JOIN users u ON t.user_id = u.id
            WHERE t.region_id = ?
        """, (region_id,)).fetchall()
        return [dict(r) for r in rows]

def get_tomb_items(tomb_id: int):
    """进入墓碑空间时，拿该墓碑的所有物品"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT i.*, ti.placed_by, ti.obtained_at
            FROM tomb_items ti
            JOIN items i ON ti.item_id = i.id
            WHERE ti.tomb_id = ?
        """, (tomb_id,)).fetchall()
        return [dict(r) for r in rows]
    


def create_user_with_tomb(username: str, password: str, region_id: str, display_name: str, epitaph: str):
    """注册即建墓碑，原子操作"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    with get_conn() as conn:
        try:
            # 先建用户
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid
            
            # 同时建墓碑
            cursor2 = conn.execute(
                "INSERT INTO tombs (user_id, region_id, display_name, epitaph) VALUES (?, ?, ?, ?)",
                (user_id, region_id, display_name, epitaph)
            )
            tomb_id = cursor2.lastrowid
            
            conn.commit()
            return {"user_id": user_id, "tomb_id": tomb_id}
        
        except sqlite3.IntegrityError:
            return None  # username已存在


def attempt_steal(thief_id: int, target_tomb_id: int, item_id: int):
    """
    盗取逻辑
    成功率由三个因素决定:
      - 物品稀有度 rarity (1-5): 越高越难偷
      - 墓碑守护等级 guardian_level: 越高越难偷
      - 盗贼阴德值 soul_reputation: 越高越容易成功

    成功率 = 50% - 稀有度惩罚 - 守护惩罚 + 阴德加成
    最终限制在 5% ~ 85% 之间
    """
    with get_conn() as conn:

        # 1. 检查物品是否真的在目标墓碑里
        item = conn.execute("""
            SELECT i.rarity FROM tomb_items ti
            JOIN items i ON ti.item_id = i.id
            WHERE ti.tomb_id = ? AND ti.item_id = ?
        """, (target_tomb_id, item_id)).fetchone()

        if not item:
            return {"error": "物品不存在或已被取走"}

        # 2. 拿守护等级和盗贼阴德值
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
        reputation = thief["soul_reputation"] # 0-200, 初始100

        # 3. 计算成功率
        # 基础成功率50%，稀有度和守护降低，阴德提升
        base = 0.5
        rarity_penalty   = (rarity - 1) * 0.08    # 最多 -0.32
        guardian_penalty = guardian * 0.04         # 每级 -4%
        rep_bonus = (reputation - 100) * 0.001     # 阴德100以上加分，以下扣分

        success_rate = base - rarity_penalty - guardian_penalty + rep_bonus
        success_rate = max(0.05, min(0.85, success_rate))  # 限制在5%-85%

        success = random.random() < success_rate

        # 4. 记录日志
        conn.execute("""
            INSERT INTO theft_logs (thief_id, target_tomb_id, item_id, success)
            VALUES (?, ?, ?, ?)
        """, (thief_id, target_tomb_id, item_id, int(success)))

        if success:
            # 把物品从目标墓碑转移到盗贼墓碑
            thief_tomb = conn.execute(
                "SELECT id FROM tombs WHERE user_id = ?", (thief_id,)
            ).fetchone()

            conn.execute("""
                UPDATE tomb_items SET tomb_id = ?, placed_by = ?
                WHERE tomb_id = ? AND item_id = ?
            """, (thief_tomb["id"], thief_id, target_tomb_id, item_id))

            # 阴德小幅下降（偷东西终究不道德）
            conn.execute(
                "UPDATE users SET soul_reputation = MAX(0, soul_reputation - 5) WHERE id = ?",
                (thief_id,)
            )

            conn.commit()
            return {
                "success": True,
                "message": "盗取成功，物品已转入你的空间",
                "success_rate": round(success_rate, 2)
            }

        else:
            # 失败惩罚
            penalty = _apply_theft_penalty(conn, thief_id, rarity)
            conn.commit()
            return {
                "success": False,
                "message": "盗取失败",
                "penalty": penalty,
                "success_rate": round(success_rate, 2)
            }


def _apply_theft_penalty(conn, thief_id: int, rarity: int):
    """
    失败惩罚，稀有度越高惩罚越重
    rarity 1-2: 仅阴德下降
    rarity 3:   标记盗墓贼 + 阴德下降
    rarity 4-5: 标记盗墓贼 + 阴德大幅下降 + 自己墓碑随机丢失一件物品
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
        # 从盗贼自己的墓碑随机拿走一件物品
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

    penalty_desc = f"阴德 -{rep_loss}"
    if rarity >= 3:
        penalty_desc += " · 被标记为盗墓贼"
    if lost_item:
        penalty_desc += f" · 你的『{lost_item}』被鬼索回"

    return penalty_desc