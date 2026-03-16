# Gym Booking App

Aplikasi booking kelas gym dengan backend FastAPI dan frontend Streamlit yang terintegrasi dengan AI agent (OpenAI Agents SDK + LiteLLM).

## Tech Stack

- **Backend:** FastAPI, SQLModel, Alembic
- **Frontend/UI:** Streamlit
- **AI Agent:** OpenAI Agents SDK, LiteLLM
- **Database:** SQLite

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Setup database

Jalankan Alembic migration untuk membuat schema database (SQLite):

```bash
alembic upgrade head
```

### 3. Seed database dengan data dummy

Jalankan script `seed_db.py` untuk generate 20 jadwal kelas gym dummy

```bash
python seed_db.py
```

atau:

```bash
make seed
```

### 4. Jalankan backend server

```bash
uvicorn app.main:app --reload
```

atau:

```bash
make server
```

### 5. Jalankan UI (Streamlit)

Di terminal terpisah, jalankan:

```bash
streamlit run streamlit_app.py
```

atau:

```bash
make streamlit
```

Aplikasi Streamlit akan terbuka di browser pada `http://localhost:8501`.

## Makefile Commands

| Command            | Deskripsi                          |
| ------------------ | ---------------------------------- |
| `make seed`        | Seed database dengan data dummy    |
| `make server`      | Start FastAPI backend              |
| `make streamlit`   | Start Streamlit frontend           |
