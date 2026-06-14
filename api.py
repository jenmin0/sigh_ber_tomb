from dotenv import load_dotenv
import os 
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from pathlib import Path
import hashlib

load_dotenv()

FAL_API_KEY = os.getenv("FAL_API_KEY")
DEEPMIND_API_KEY = os.getenv("DEEPMIND_API_KEY")

# Make sure to replace the above with your actual API keys in the .env file, and never commit real keys to version control!
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


app.mount("/static", StaticFiles(directory="src/data"), name="static")


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
        # Count tombs in this region for the histogram, with a fallback to a random number if the database is empty (for demo purposes)
        try:
            with get_conn() as conn:
                count = conn.execute(
                    "SELECT COUNT(*) FROM tombs WHERE region_id = ?", (r["id"],)
                ).fetchone()[0]
        except Exception:
            # If there's any issue with the database (like it's not initialized yet), just return a random count for demo purposes
            import random
            count = random.randint(5, 45) 

        # 2. Compatibility handling for coordinates: support both "coordinates": [lng, lat] and separate "lat", "lng" fields
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
                   t.region_id, u.email, u.is_thief
            FROM tombs t 
            LEFT JOIN users u ON t.user_id = u.id
            WHERE t.lat IS NOT NULL AND t.lng IS NOT NULL
        """).fetchall()
        return [dict(r) for r in rows]

@app.get("/tombs/{tomb_id}/items")
def tomb_items(tomb_id: int):
    return get_tomb_items(tomb_id)


class RegisterRequest(BaseModel):
    email: str
    password: str
    region_id: str
    display_name: str
    epitaph: str = ""
    lat: float = 0.0
    lng: float = 0.0


@app.post("/register")
def register(req: RegisterRequest):
    result = create_user_with_tomb(
        req.email, req.password, req.region_id, req.display_name, req.epitaph, req.lat, req.lng

    )
    if result is None:
        return {"error": "Email already exists"}
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
    tomb_id: str, message: str = Query(..., description="The message from the visitor to the digital soul in the tomb. Keep it concise and respectful.")
):
    # An optional function to generate a witty, slightly eerie response from the perspective of the digital soul resting in the tomb, using Gemini 1.5 Flash. The system instruction sets the tone and style of the response, and we ensure to handle any potential errors gracefully, returning a fallback message if the AI call fails.
    system_instruction = f"""
    You are the digital soul of the tomb with ID {tomb_id}, resting in the afterlife. Respond to the visitor's 
    message with a tone that is respectful, slightly eerie, and infused with a touch of ancient wisdom. Your 
    reply should be concise, ideally under 50 words, and evoke a sense of mystery and timelessness. You 
    can reference the burial culture or region associated with your tomb if relevant, but always maintain 
    an enigmatic and poetic style in your response.
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
            "reply": "[The digital soul is silent for now... Try again later to hear its whispers.]"
        }


# ----------------- Main Page -----------------
@app.get("/", response_class=HTMLResponse)
def get_main_page():
    # Return the main HTML page for the front-end. Make sure to create an index.html file in the same directory as this api.py with your front-end code. This allows us to serve the front-end directly from the FastAPI backend, simplifying deployment and development.
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>Please create an index.html file in the same directory as this api.py</h3>"
    


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(req: LoginRequest):
    email = req.email
    password = req.password
    
    # Encrypt the password using SHA-256 before comparing with the database
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        with get_conn() as conn:
            # Send the email and the hashed password to the database for verification
            row = conn.execute("""
                SELECT t.id, t.display_name, t.region_id, t.epitaph, t.shape, t.color, u.id as user_id
                FROM tombs t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE u.email = ? AND u.password_hash = ?
            """, (email, password_hash)).fetchone()  # Use the hashed password in the query
            
            if not row:
                return {"error": f"Login failed. Account {email} not found or password incorrect."}
                
            return {
                "id": row["id"],               # global tomb id
                "user_id": row["user_id"],     
                "tomb_id": row["id"], 
                "display_name": row["display_name"],
                "tomb": {
                    "id": row["id"],
                    "display_name": row["display_name"],
                    "region_id": row["region_id"],
                    "epitaph": row["epitaph"],
                    "shape": row["shape"] or "arch",
                    "color": row["color"] or "#c9a874"
                }
            }
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}
    
class SacrificeRequest(BaseModel):
    item_name: str
    user_id: int

@app.post("/tombs/{tomb_id}/sacrifice")
async def sacrifice_to_tomb(tomb_id: int, req: SacrificeRequest):

    prompt = f"low-poly illustration of {req.item_name}, geometric facets, muted earthy tones, soft lighting, isolated object on transparent background, game asset style"
    
    image_url = None
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://fal.run/fal-ai/flux/schnell",  # Synchronous endpoint for faster response, suitable for simple image generation tasks
                headers={"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"},
                json={"prompt": prompt, "image_size": "square_hd"},
                timeout=30.0
            )
            print(f"Fal status: {res.status_code}, body: {res.text[:200]}")
            if res.status_code == 200:
                image_url = res.json().get("images", [{}])[0].get("url")
    except Exception as e:
        print(f"Fal failed: {e}")

    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, description, rarity, image_url) VALUES (?, ?, ?, ?)",
            (req.item_name, f"A {req.item_name} placed in this tomb space", 2, image_url)
        )
        item_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO tomb_items (tomb_id, item_id, placed_by) VALUES (?, ?, ?)",
            (tomb_id, item_id, req.user_id)
        )
        conn.commit()

    return {
        "success": True,
        "item_id": item_id,
        "image_url": image_url,
        "message": f"'{req.item_name}' has been placed in the tomb space."
    }

