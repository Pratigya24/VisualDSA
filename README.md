# VisualDSA AI

An AI-powered, visualization-first platform for learning Data Structures &
Algorithms. See `docs/01-architecture.md` for the full architecture, SRS,
API design, and roadmap this codebase implements.

## Status

- ✅ **Module 1 — Foundation & Authentication** (JWT + Google OAuth, protected routing, design system)
- ✅ **Module 2 — DSA Learning Platform Foundation** (Dashboard, Roadmap, Progress, Bookmarks, Notes, Profile)
- ⏳ Module 3 — Algorithm Engine & Plugin System
- ⏳ Module 4 — Visualization Engine (X-Ray Mode)
- ⏳ Module 5 — Dry Run & Debugging Engine
- ⏳ Module 6 — AI Learning Engine
- ⏳ Module 7 — Advanced Learning & Deployment

## Prerequisites

- Python 3.12+
- Node.js 20+
- MongoDB (local instance or Atlas connection string)
- Redis (local instance, e.g. `docker run -p 6379:6379 redis`)

## Backend setup

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv
bash scripts/generate_dev_keys.sh                          # generates local JWT RSA keypair
cp .env.example .env                                       # fill in MONGODB_URI, GOOGLE_CLIENT_ID, etc.
python -m scripts.seed_content                              # seeds topics + problem catalog
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs

Run tests: `python -m pytest tests/ -v`

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env                # set VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

App: http://localhost:5173

Run checks: `npm run typecheck && npm run lint && npm test`

## Docker Compose (both services + Mongo + Redis)

```bash
docker compose up --build
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full list.
At minimum for local dev you need `MONGODB_URI`, `JWT_PRIVATE_KEY` /
`JWT_PUBLIC_KEY` (from `generate_dev_keys.sh`), and `REDIS_URL`. Google OAuth
and the AI provider keys (`OPENAI_API_KEY` / `GEMINI_API_KEY`, needed from
Module 6 onward) are optional until you use those features.

## Project structure

```
backend/   FastAPI, Clean Architecture (api → services → engines → repositories → models)
frontend/  React 19 + TS + Vite, feature-based architecture
docs/      Architecture, SRS, API design, roadmap
```
