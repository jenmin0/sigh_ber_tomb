# ⬡ Cyber Cemetery — *Sigh_ber_tomb*

> *"I was here. I loved. I faded."*

A geo-social digital afterlife platform where users choose a burial tradition, plant their tomb anywhere on Earth, and build a persistent cyber space — filled with AI-generated offerings, left by the living and taken by the bold.

---

## Concept

Cyber Cemetery maps the world's burial cultures and invites users to engage with death as a design question: *Where would you want to rest, and how?*

Each user registers by selecting a burial tradition (sky burial in Qinghai, fantasy coffins in Ghana, green burial in Norway...) and pinning their tomb to a coordinate on the world map. Their tomb becomes a personal space — decoratable, visitable, and vulnerable to digital grave robbers.

---

## Features

### ✅ Implemented

- **World Burial Culture Map** — Hover over any country to browse its burial traditions, sourced from a curated dataset of 20+ global practices
- **Tomb Placement (Registration)** — Select a burial culture, pin a coordinate, fill in your name and epitaph. One account, one tomb
- **User Login** — Email + password authentication
- **Tomb Customization** — Change your tomb's shape (arch, obelisk, cross) and color
- **AI-Generated Offerings** — Describe any object; Fal generates a low-poly illustration and places it in your tomb space
- **Leave Gifts** — Visit another user's tomb and leave an offering
- **Steal Items** — Attempt to take items from other tombs. Success rate depends on item rarity, tomb guardian level, and your soul reputation. Failure has consequences
- **Vote for proposals** — Community proposals to build tombs for public figures

### 🐞 Bugs to Fix

- Users who register before creating a tomb are currently unable to create one afterward
- Unregistered visitors can currently leave gifts to other users' tombs
- Failure to Pin/Locate Tombs for Approved Proposals on Main Map
- Proposal Persistence Post-Voting


### 🚧 Not Yet Implemented

- Visitor messages / guestbook
- Cyber ghost replies via Google DeepMind (Gemini) — the tomb owner's digital remnant responding to visitors
- Item/gift economy with actual user balance tracking

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python |
| Database | SQLite via `sqlite3` |
| Frontend | Vanilla HTML/CSS/JS + D3.js + TopoJSON |
| Map | D3 Natural Earth projection, world-atlas GeoJSON |
| AI Image Generation | Fal (`fal-ai/flux/schnell`) |
| AI Ghost (planned) | Google Gemini (DeepMind) |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/jenmin0/sigh_ber_tomb.git
cd sigh_ber_tomb
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv myenv

# Windows
myenv\Scripts\activate

# macOS / Linux
source myenv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
FAL_API_KEY=your_fal_api_key
DEEPMIND_API_KEY=your_gemini_api_key
```

> ⚠️ Never commit `.env` to version control. It is listed in `.gitignore`.

### 4. Initialize the database

```bash
python .\src\init_db.py
```


---

## Running the App

### Start the backend API

```bash
uvicorn api:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Open the frontend

Open `index.html` directly in your browser (double-click or drag into Chrome/Firefox).

> The frontend calls `http://localhost:8000` for all data. Keep uvicorn running in the background.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/regions` | All burial culture regions |
| `GET` | `/burial-cultures` | Full burial culture dataset |
| `GET` | `/tombs` | All placed tombs with coordinates |
| `GET` | `/tombs/{tomb_id}/items` | Items in a tomb space |
| `POST` | `/register` | Create user + place tomb |
| `POST` | `/login` | Authenticate user |
| `POST` | `/tombs/{id}/sacrifice` | Generate and place an item (via Fal) |
| `POST` | `/tombs/{id}/appearance` | Update tomb shape and color |
| `POST` | `/steal` | Attempt to steal an item from a tomb |

---

## Project Structure

```
sigh_ber_tomb/
├── api.py                  # FastAPI app and all routes
├── index.html              # Frontend (map, tomb space, all UI)
├── requirements.txt
├── .env                    # API keys (not committed)
├── .gitignore
└── src/
    ├── db.py               # Database connection and queries
    ├── init_db.py          # Schema creation and initial data
    ├── seed_demo_tombs.py      # Demo data seeder
    └── data/
        ├── burial_data.json    # Burial culture dataset
        └── background.png      # Tomb space background image
```

---

## Partner Technologies

| Partner | Usage |
|---------|-------|
| **Fal** | Real-time low-poly image generation for tomb offerings |
| **Google DeepMind** | Planned: Gemini-powered cyber ghost for visitor interactions |

---

## Team
@Li Min, @Xinran Yin

Built at AI Hackathon 2026.
