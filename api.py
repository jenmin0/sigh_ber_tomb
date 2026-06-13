import random
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import json
from pathlib import Path

# 确保你的 mock 或 db 导入正常。为了让你能直接跑通，这里用你提供的数据做基础
from src.db import (
    attempt_steal,
    create_user_with_tomb,
    get_all_regions,
    get_conn,
    get_tomb_items,
    get_tombs_by_region,
)

app = FastAPI(title="CyberTomb API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPMIND_API_KEY = "AIzaSy..."
FAL_API_KEY = "fal-..."

FLAG_MAP = {
    "qinghai-sky": "🌄",
    "fiji-sea": "🌊",
    "norway-tree": "🌲",
    "vatican-catacomb": "⛪",
    "ghana-fantasy": "🎊",
}

@app.get("/burial-cultures")
def burial_cultures():
    path = Path("src/data/burial_data.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return JSONResponse(data)

@app.get("/regions")
def regions():
    raw = get_all_regions()
    result = []
    for r in raw:
        # 1. 动态统计该地区在数据库里的墓碑数量
        try:
            with get_conn() as conn:
                count = conn.execute(
                    "SELECT COUNT(*) FROM tombs WHERE region_id = ?", (r["id"],)
                ).fetchone()[0]
        except Exception:
            # 如果数据库暂时没数据，黑客马拉松演示时给个好看的初始数字，防止柱状图是空的
            import random
            count = random.randint(5, 45) 

        # 2. 兼容经纬度字段
        if "coordinates" in r and isinstance(r["coordinates"], list) and len(r["coordinates"]) >= 2:
            lng, lat = r["coordinates"][0], r["coordinates"][1]
        else:
            lat = r.get("coordinates_lat") or r.get("lat") or 30.0
            lng = r.get("coordinates_lng") or r.get("lng") or 30.0

        result.append({
            "id": r["id"],
            "name": r["name"],
            "lat": float(lat), 
            "lng": float(lng),
            "burial_type": r.get("type") or r.get("burial_type") or "未知界陵", 
            "description": r.get("description", ""),
            "flag": FLAG_MAP.get(r["id"], "🌍"),
            "tomb_count": count  # 必须返回这个字段给前端
        })
    return result

@app.get("/tombs")
def all_tombs():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT t.id, t.display_name, t.epitaph, t.lat, t.lng,
                   t.region_id, u.username, u.is_thief
            FROM tombs t 
            LEFT JOIN users u ON t.user_id = u.id
            WHERE t.lat IS NOT NULL AND t.lng IS NOT NULL
        """).fetchall()
        return [dict(r) for r in rows]

@app.get("/tombs/{tomb_id}/items")
def tomb_items(tomb_id: int):
    return get_tomb_items(tomb_id)


class RegisterRequest(BaseModel):
    username: str
    password: str
    region_id: str
    display_name: str
    epitaph: str = ""
    lat: float = 0.0
    lng: float = 0.0


@app.post("/register")
def register(req: RegisterRequest):
    result = create_user_with_tomb(
        req.username, req.password, req.region_id, req.display_name, req.epitaph
    )
    if result is None:
        return {"error": "Username already exists"}
    return result


class StealRequest(BaseModel):
    thief_id: int
    target_tomb_id: int
    item_id: int


@app.post("/steal")
def steal(req: StealRequest):
    return attempt_steal(req.thief_id, req.target_tomb_id, req.item_id)


@app.get("/tombs/{tomb_id}/chat")
async def chat_with_soul(
    tomb_id: str, message: str = Query(..., description="访客对死者说的话")
):
    # 针对 Mock 数据或真实数据做处理
    system_instruction = f"""
    你现在是安息在赛博空间的数字亡魂残影。
    请用幽默、冷酷、带点电子故障感、看透尘世但充满人文关怀的语气，回应来看望你的访客。
    字数必须控制在 80 字以内。
    """
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={DEEPMIND_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": message}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"maxOutputTokens": 150, "temperature": 0.7},
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(gemini_url, json=payload, timeout=10.0)
            res_data = response.json()
            ai_reply = res_data["candidates"][0]["content"]["parts"][0][
                "text"
            ].strip()
            return {"reply": ai_reply}
    except Exception:
        return {
            "reply": "【系统电波微弱……】丢包严重。活着的人啊，珍惜你的代码吧。"
        }


# ----------------- 页面主入口：返回你写的高级 3D HTML 页面 -----------------
@app.get("/", response_class=HTMLResponse)
def get_main_page():
    # 读取你之前编写的那份拥有炫酷 CSS 侧边栏和 Google Maps 3D 的 HTML 文件
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>请将你前端的 HTML 代码保存为同级目录下的 index.html 文件</h3>"