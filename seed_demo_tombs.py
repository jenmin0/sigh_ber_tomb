import sqlite3
import hashlib
import os

DB_PATH = "cybertomb.db"

DEMO_TOMBS = [
  { "id": "PH-SAG-001", "name": "Echo Valley Cliffside", "city": "Sagada, Philippines", "coordinates": [120.9022, 17.0894], "type": "Hanging Coffins" },
  { "id": "ID-TOR-002", "name": "Lemo Burial Cliff", "city": "Tana Toraja, Indonesia", "coordinates": [119.8974, -2.9775], "type": "Ma'nene & Funeral Rites" },
  { "id": "MG-AMB-003", "name": "Ambohimanga Ancestral Vault", "city": "Antananarivo, Madagascar", "coordinates": [47.5815, -18.7562], "type": "Famadihana" },
  { "id": "GH-ACC-004", "name": "Kane Kwei Carpentry Workshop", "city": "Accra, Ghana", "coordinates": [-0.1869, 5.6037], "type": "Fantasy Coffins" },
  { "id": "IN-VAR-005", "name": "Manikarnika Ghat Cremation", "city": "Varanasi, India", "coordinates": [82.9739, 25.3176], "type": "Ganges Cremation" },
  { "id": "US-FL-006", "name": "Celestis Orbital Gateway", "city": "Cape Canaveral, USA", "coordinates": [-80.6076, 28.3922], "type": "Space Burial" },
  { "id": "MX-OAX-007", "name": "Oaxaca Memorial Plaza", "city": "Oaxaca, Mexico", "coordinates": [-96.7233, 17.0732], "type": "Day of the Dead" },
  { "id": "KR-SEO-008", "name": "Bongeunsa Sacred Beads", "city": "Seoul, South Korea", "coordinates": [127.0577, 37.5134], "type": "Death Beads" },
  { "id": "IT-PAL-009", "name": "Capuchin Crypt Gallery", "city": "Palermo, Italy", "coordinates": [13.3614, 38.1157], "type": "Capuchin Catacombs Preservation" },
  { "id": "SE-GOT-010", "name": "Promessa Research Lab", "city": "Gothenburg, Sweden", "coordinates": [11.9746, 57.7089], "type": "Promession (Cryomation)" },
  { "id": "IT-MIL-011", "name": "Capsula Mundi Grove", "city": "Milan, Italy", "coordinates": [9.1900, 45.4642], "type": "Capsula Mundi (Green Burial)" },
  { "id": "JP-TOK-012", "name": "Ruriden High-Tech Vault", "city": "Tokyo, Japan", "coordinates": [139.6917, 35.6895], "type": "High-Tech Columbarium (Ruriden)" },
  { "id": "IS-REY-013", "name": "Faxaflói Marine Scatter", "city": "Reykjavik, Iceland", "coordinates": [-21.9426, 64.1466], "type": "Water Burial" },
  { "id": "US-KEY-014", "name": "Neptune Memorial Reef", "city": "Key Largo, USA", "coordinates": [-80.4473, 25.0865], "type": "Eternal Reefs (Marine Burial)" },
  { "id": "EG-GIZ-015", "name": "Great Pyramid Necropolis", "city": "Giza, Egypt", "coordinates": [31.1342, 29.9792], "type": "Mummification & Pyramids" },
  { "id": "NP-EVE-016", "name": "Khumbu Sky Burial Site", "city": "Everest Region, Nepal", "coordinates": [86.9226, 27.9881], "type": "Open-air Burial" },
  { "id": "CA-BC-017", "name": "Haida Totem Forest", "city": "Haida Gwaii, Canada", "coordinates": [-132.1221, 53.2500], "type": "Indigenous Platform Burial" },
  { "id": "CN-BO-018", "name": "Bo People Hanging Site", "city": "Gongxian, China", "coordinates": [104.7200, 28.1400], "type": "Boat-shaped Hanging Coffins" },
  { "id": "US-LA-019", "name": "Alkaline Hydrolysis Center", "city": "Los Angeles, USA", "coordinates": [-118.2437, 34.0522], "type": "Resomation (Alkaline Hydrolysis)" },
  { "id": "CH-ZUR-020", "name": "Algordanza Diamond Studio", "city": "Zurich, Switzerland", "coordinates": [8.5417, 47.3769], "type": "Memorial Diamonds" },
]

EPITAPHS = [
    "Here the data rests, but the signal endures.",
    "I was compiled once. I shall not be garbage collected.",
    "Uploaded to the void. Ping me sometime.",
    "My last commit. No more pull requests.",
    "404: Soul not found. Still searching.",
    "Kernel panic. Rebooting elsewhere.",
    "The loop ended. The memory remains.",
    "Offline for eternity. DMs are closed.",
    "I left no bugs. Only mysteries.",
    "Defragged and departing. Storage: freed.",
    "Connection timed out. Retrying in another life.",
    "Deprecated, but never forgotten.",
    "The process exited gracefully.",
    "My stack overflowed with love.",
    "Root access revoked. Rest now.",
    "End of file. Begin of legend.",
    "I ran out of entropy.",
    "Segmentation fault in sector: heart.",
    "The server is down. The soul is up.",
    "Checksum verified. Journey complete.",
]

def seed():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    inserted = 0
    skipped = 0

    for i, tomb in enumerate(DEMO_TOMBS):
        username = f"system_{tomb['id'].lower()}"
        password_hash = hashlib.sha256(b"demo_system_account").hexdigest()
        lng, lat = tomb["coordinates"]
        epitaph = EPITAPHS[i % len(EPITAPHS)]

        try:
            # 插入系统用户
            cur = c.execute(
                "INSERT INTO users (username, password_hash, soul_reputation) VALUES (?, ?, ?)",
                (username, password_hash, 999)
            )
            user_id = cur.lastrowid

            # 插入墓碑
            c.execute(
                """INSERT INTO tombs (user_id, region_id, display_name, epitaph, lat, lng)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, tomb["id"], tomb["name"], epitaph, lat, lng)
            )
            inserted += 1
            print(f"  ✓ {tomb['name']} ({tomb['city']})")

        except sqlite3.IntegrityError:
            skipped += 1
            print(f"  - skipped (already exists): {username}")

    conn.commit()
    conn.close()
    print(f"\nDone. {inserted} tombs inserted, {skipped} skipped.")

if __name__ == "__main__":
    seed()