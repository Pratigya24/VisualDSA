# VisualDSA AI — Architecture & Planning Document

**Phase:** 0 — Pre-Development Architecture (no code, per workflow contract)
**Status:** Draft for approval
**Version:** 1.0

---

## Table of Contents

1. Software Requirements Specification (SRS)
2. System Architecture Document
3. High-Level Architecture Diagram
4. Database ER Diagram
5. Folder Structure
6. API Design
7. Feature Roadmap
8. Development Milestones
9. Component Hierarchy
10. Database Schema
11. Deployment Architecture
12. Security Architecture
13. State Management Strategy
14. AI Engine Design
15. Visualization Engine Design
16. Plugin Architecture

---

## 1. Software Requirements Specification (SRS)

### 1.1 Purpose

VisualDSA AI is a web platform that teaches Data Structures & Algorithms through
synchronized, state-driven visualizations combined with an AI mentor layer. The
platform's differentiator against LeetCode / NeetCode / AlgoExpert / Visualgo /
GeeksforGeeks is **simultaneous multi-panel understanding**: code, visualization,
memory model, and AI explanation update from a single source of truth (a
"visualization state timeline") rather than four disconnected tools.

### 1.2 Scope

In scope for v1 (Phases 1–7 of this build):

- Auth (email/password + Google OAuth), profile, dashboard
- Roadmap, progress tracking, bookmarks, notes, revision planner, flashcards
- Plugin-based Algorithm Engine covering the 20 categories listed by the client
- Visualization Engine driven by generated state timelines (no hardcoded animation)
- Dry Run Engine (step-by-step execution trace: variables, pointers, call stack, heap)
- AI Engine: problem explainer, concept teacher, code explainer, debugger,
  mentor chat, pattern detector, solution comparator
- Interview Mode (timed, AI-graded), Contest Mode, Leaderboards, Achievements
- Company-wise question banks, Mind Maps, Whiteboard
- Analytics/history, Notification-free (deferred), no payments in v1

Out of scope for v1 (explicitly deferred, flagged so scope doesn't silently creep):

- Native mobile apps (web is responsive, not packaged)
- Payments/subscriptions billing
- Real-time multiplayer contests (v1 contest mode is asynchronous, leaderboard-based)
- Video content authoring tools

### 1.3 Actors

| Actor | Description |
|---|---|
| Guest | Unauthenticated visitor; can browse public roadmap/marketing pages only |
| Student | Primary user; solves problems, uses AI mentor, tracks progress |
| Admin | Manages algorithm content, moderates, views platform analytics |
| System (AI Engine) | Automated actor invoked by Student actions; produces explanations, grades interviews |

### 1.4 Functional Requirements (representative, by module)

**FR-AUTH**
- FR-AUTH-1: User can register with email/password (bcrypt-hashed, verified via email token)
- FR-AUTH-2: User can log in via Google OAuth 2.0
- FR-AUTH-3: System issues short-lived JWT access tokens (15 min) + rotating refresh tokens (7 days, httpOnly cookie)
- FR-AUTH-4: User can reset password via emailed one-time token

**FR-DASH**
- FR-DASH-1: Dashboard shows streak, weekly activity heatmap, topic mastery radar, recommended next problem
- FR-DASH-2: Dashboard data is served from a single aggregated endpoint (no N+1 client calls)

**FR-ALGO**
- FR-ALGO-1: Every algorithm is registered as a plugin implementing a common `AlgorithmPlugin` interface (see §16)
- FR-ALGO-2: Running a plugin against input produces an ordered list of `VisualizationState` objects (see §15)
- FR-ALGO-3: User can step forward/back, play/pause/scrub through states at variable speed

**FR-DRYRUN**
- FR-DRYRUN-1: Dry Run Engine executes user or reference code in a sandboxed subprocess and emits a trace: line number, locals, call stack frame, heap allocations, recursion depth
- FR-DRYRUN-2: Recursion Tree view derives from the call-stack trace, not a separate hand-authored animation

**FR-AI**
- FR-AI-1: Each AI feature (explainer, debugger, mentor, pattern detector, comparator) is a distinct prompt template + typed response schema (see §14)
- FR-AI-2: AI responses are streamed to the client (SSE) for perceived latency
- FR-AI-3: AI provider is swappable (OpenAI GPT / Google Gemini) behind a single `AIProvider` interface; failover from primary to secondary provider on error/timeout

**FR-INTERVIEW**
- FR-INTERVIEW-1: Interview Mode presents a timed problem, records code + a transcript of AI follow-up Q&A, and produces an AI-generated Interview Report (correctness, complexity, communication score, rubric-based)

**FR-PROGRESS**
- FR-PROGRESS-1: Every problem attempt is recorded (status, time spent, hints used, complexity submitted) for analytics and spaced-repetition scheduling

### 1.5 Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | P95 API latency < 300ms for non-AI endpoints; visualization state generation for arrays up to 10k elements < 500ms server-side |
| Scalability | Stateless API pods behind a load balancer; horizontal scaling via container replicas; Celery workers scale independently for AI/dry-run jobs |
| Availability | 99.5% target; graceful degradation — if AI provider is down, visualization/dry-run features still work |
| Security | OWASP ASVS L2 baseline; sandboxed code execution (no network, memory/CPU/time-limited); JWT + refresh rotation; rate limiting per user and per IP |
| Accessibility | WCAG 2.1 AA; full keyboard navigation of the visualizer; screen-reader labels on all SVG/canvas visual elements via ARIA live regions summarizing state changes |
| Maintainability | Clean Architecture layering (§2); plugin architecture so new algorithms/AI prompts ship without touching core engines |
| Observability | Structured logging, request tracing (correlation ID), metrics (Prometheus-compatible), error tracking (Sentry) |

### 1.6 Constraints

- Sandboxed code execution must never allow filesystem/network access from user code
- AI calls must never receive PII beyond what's required for the prompt
- MongoDB is the system of record; Redis is cache/session/broker only (not durable)

---

## 2. System Architecture Document

### 2.1 Architectural Style

**Clean Architecture**, layered, with a **plugin architecture** for the two most
volatile subsystems (Algorithms, AI Prompts), so new content ships without
modifying core engine code (Open/Closed Principle).

Backend layering (dependency direction: outer → inner, inner layers know nothing
about outer layers):

```
┌─────────────────────────────────────────────────────────┐
│ api/            (FastAPI routers — HTTP boundary)        │
├─────────────────────────────────────────────────────────┤
│ services/       (use-case orchestration, business logic) │
├─────────────────────────────────────────────────────────┤
│ engines/        (Algorithm Engine, Visualization Engine, │
│                  Dry Run Engine, AI Engine — domain core) │
├─────────────────────────────────────────────────────────┤
│ repositories/   (data access, Beanie/Motor abstractions) │
├─────────────────────────────────────────────────────────┤
│ models/         (Beanie ODM documents — MongoDB schema)  │
└─────────────────────────────────────────────────────────┘
   cross-cutting: core/ (config, security, deps), middleware/, utils/, schemas/ (Pydantic DTOs), prompts/ (AI templates)
```

Rules enforced by this layering:

- `api/` depends only on `services/` (via Pydantic `schemas/` DTOs, never raw ODM models)
- `services/` orchestrates `engines/` + `repositories/`, contains no HTTP or DB-driver-specific code
- `engines/` are pure domain logic — an `engines/algorithms/` plugin never imports FastAPI or Motor
- `repositories/` is the only layer that imports Beanie/Motor directly
- Swapping MongoDB for another store only touches `repositories/` + `models/`
- Swapping OpenAI for Gemini only touches `engines/ai/providers/`

Frontend layering (feature-based, not type-based, to keep features independently deletable/shippable):

```
features/<feature>/
  components/   feature-scoped UI
  hooks/        feature-scoped hooks (data fetching via TanStack Query)
  api/          feature-scoped Axios calls + query keys
  store/        feature-scoped Zustand slice (if needed)
  types.ts
shared/
  components/   design-system primitives (shadcn-based)
  hooks/
  utils/
```

### 2.2 Key Architectural Decisions (ADR summary)

| Decision | Rationale |
|---|---|
| MongoDB over relational DB | Algorithm/visualization state documents are naturally nested/variable-shape (heap snapshots, call stacks differ per algorithm); document model avoids excessive joins |
| Beanie (ODM) over raw Motor | Type-safe Pydantic-backed models, less boilerplate, still exposes Motor for advanced aggregation pipelines when needed |
| Visualization states generated server-side | Guarantees frontend never hardcodes algorithm-specific animation logic (client requirement); also allows the exact same trace to power AI explanations, since the AI reads the same state timeline |
| Redis + Celery for AI/dry-run jobs | AI calls and sandboxed code execution are unbounded-latency operations; they must not block the request/response cycle of the API pod |
| JWT + refresh rotation over session cookies alone | Enables stateless horizontal scaling of API pods while still allowing revocation via a Redis-backed refresh-token denylist |
| Plugin architecture for Algorithms and AI Prompts | These two subsystems grow continuously (new algorithms, new prompt types); plugins let them grow via addition, not modification |
| Sandboxed subprocess (not eval) for Dry Run Engine | User-submitted code must never execute with the API process's privileges |

### 2.3 System Context (C4 Level 1)

```
                      ┌────────────────────┐
                      │      Student        │
                      └──────────┬──────────┘
                                 │ HTTPS
                                 ▼
                      ┌────────────────────┐
                      │   VisualDSA AI Web  │ (React SPA, Vercel)
                      └──────────┬──────────┘
                                 │ REST/SSE (HTTPS)
                                 ▼
                      ┌────────────────────┐
                      │  VisualDSA AI API   │ (FastAPI, Render/Railway)
                      └──┬──────┬───────┬───┘
                         │      │       │
             ┌───────────┘  ┌───┘   ┌───┘
             ▼               ▼       ▼
      ┌────────────┐ ┌─────────────┐ ┌──────────────────┐
      │ MongoDB     │ │ Redis        │ │ Celery Workers    │
      │ Atlas       │ │ (cache/queue)│ │ (AI + Dry Run jobs)│
      └────────────┘ └─────────────┘ └─────┬─────────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                        ┌──────────┐  ┌───────────┐  ┌─────────────┐
                        │ OpenAI    │  │ Gemini     │  │ Sandboxed    │
                        │ GPT API   │  │ API        │  │ Exec Runner  │
                        └──────────┘  └───────────┘  └─────────────┘
```

---

## 3. High-Level Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Browser)                          │
│  React 19 + TS + Vite SPA                                              │
│  Router → Feature Modules → Zustand (client state) + TanStack Query     │
│  (server-state cache) → Axios → API                                    │
│  Rendering: React Flow (graphs/trees), Recharts (complexity/analytics),│
│  Monaco (code editor), Framer Motion (transitions)                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTPS (REST) + SSE (AI streaming)
┌───────────────────────────────▼─────────────────────────────────────┐
│                         NGINX (reverse proxy / TLS)                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                 │
┌───────────────────────────────▼─────────────────────────────────────┐
│                          FastAPI Application                          │
│ ┌────────┐ ┌─────────────┐ ┌────────────────────────┐ ┌────────────┐│
│ │ api/   │→│ services/    │→│ engines/                │→│repositories││
│ │routers │ │ use-cases    │ │ • algorithm plugins     │ │  (Beanie)  ││
│ └────────┘ └─────────────┘ │ • visualization engine  │ └─────┬──────┘│
│                             │ • dry-run engine        │       │       │
│                             │ • ai engine + prompts   │       │       │
│                             └───────────┬─────────────┘       │       │
│ middleware/: auth, rate-limit, CORS, request-id, error-handler│       │
└─────────────────────────────────────────┼─────────────────────┼──────┘
                                 │(enqueue)│                     │
                    ┌────────────▼────┐    │           ┌────────▼────────┐
                    │ Redis (broker +  │    │           │  MongoDB Atlas   │
                    │ cache + sessions)│    │           │  (system of      │
                    └────────┬─────────┘    │           │   record)        │
                              │              │           └─────────────────┘
                    ┌─────────▼────────┐    │
                    │ Celery Workers    │◄───┘
                    │ • ai_tasks        │
                    │ • dryrun_tasks    │
                    │ • analytics_tasks │
                    └───────────────────┘
```

---

## 4. Database ER Diagram

```
┌───────────────┐        ┌────────────────┐        ┌────────────────┐
│ users          │1      *│ progress        │*      1│ algorithms      │
│ _id            │────────│ user_id (FK)    │────────│ _id             │
│ email          │        │ algorithm_id(FK)│        │ slug            │
│ password_hash  │        │ status          │        │ title           │
│ oauth_provider │        │ attempts        │        │ topic_id (FK)   │
│ display_name   │        │ best_time_ms    │        │ difficulty      │
│ avatar_url     │        │ last_attempt_at │        │ plugin_key      │
│ role           │        └────────┬────────┘        │ companies[]     │
│ created_at     │                 │                  └────────┬────────┘
└──────┬─────────┘                 │                           │
       │1                          │*                          │*
       │                    ┌──────▼─────────┐          ┌──────▼─────────┐
       │*                   │ history         │          │ topics          │
┌──────▼─────────┐          │ user_id (FK)    │          │ _id             │
│ bookmarks       │          │ algorithm_id(FK)│          │ name            │
│ user_id (FK)    │          │ action          │          │ order           │
│ algorithm_id(FK)│          │ payload         │          │ prerequisite_ids│
│ created_at      │          │ created_at      │          └─────────────────┘
└─────────────────┘          └─────────────────┘
       │1                                                       │1
       │*                                                       │*
┌──────▼─────────┐   ┌─────────────────┐   ┌─────────────────┐ ┌▼────────────────┐
│ notes           │   │ chats            │   │ interview_reports│ │ flashcards       │
│ user_id (FK)    │   │ user_id (FK)     │   │ user_id (FK)     │ │ user_id (FK)     │
│ algorithm_id(FK)│   │ algorithm_id(FK) │   │ algorithm_id(FK) │ │ algorithm_id(FK) │
│ content_md      │   │ messages[]       │   │ transcript[]     │ │ front / back     │
│ updated_at      │   │ ai_provider      │   │ scores{}         │ │ srs_due_at       │
└─────────────────┘   │ created_at       │   │ created_at       │ └──────────────────┘
                       └──────────────────┘   └──────────────────┘

┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ achievements     │   │ revision_plans    │   │ mind_maps        │
│ user_id (FK)     │   │ user_id (FK)      │   │ user_id (FK)     │
│ badge_key        │   │ scheduled_items[] │   │ topic_id (FK)    │
│ earned_at        │   │ cadence           │   │ nodes[] / edges[]│
└─────────────────┘   └──────────────────┘   └─────────────────┘

┌─────────────────┐
│ analytics_events │  (append-only, TTL-indexed, feeds dashboards/leaderboards)
│ user_id (FK)     │
│ event_type       │
│ metadata{}        │
│ created_at        │
└──────────────────┘
```

Relationships are logical (application-enforced), not DB-enforced FKs, per
MongoDB norms — see §10 for indexing/reference strategy.

---

## 5. Folder Structure

```
visualdsa-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── topics.py
│   │   │   │   ├── algorithms.py
│   │   │   │   ├── visualizer.py
│   │   │   │   ├── dryrun.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── bookmarks.py
│   │   │   │   ├── notes.py
│   │   │   │   ├── progress.py
│   │   │   │   ├── interview.py
│   │   │   │   ├── contest.py
│   │   │   │   ├── leaderboard.py
│   │   │   │   ├── achievements.py
│   │   │   │   ├── flashcards.py
│   │   │   │   ├── mindmaps.py
│   │   │   │   └── analytics.py
│   │   │   └── deps.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── algorithm_service.py
│   │   │   ├── visualization_service.py
│   │   │   ├── dryrun_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── progress_service.py
│   │   │   ├── interview_service.py
│   │   │   └── analytics_service.py
│   │   ├── engines/
│   │   │   ├── algorithms/
│   │   │   │   ├── base.py              # AlgorithmPlugin ABC
│   │   │   │   ├── registry.py          # plugin discovery/registration
│   │   │   │   ├── sorting/
│   │   │   │   ├── searching/
│   │   │   │   ├── linked_list/
│   │   │   │   ├── stack_queue/
│   │   │   │   ├── heap/
│   │   │   │   ├── tree/
│   │   │   │   ├── bst/
│   │   │   │   ├── trie/
│   │   │   │   ├── graph/
│   │   │   │   ├── dp/
│   │   │   │   ├── greedy/
│   │   │   │   ├── backtracking/
│   │   │   │   ├── sliding_window/
│   │   │   │   ├── two_pointer/
│   │   │   │   ├── union_find/
│   │   │   │   ├── segment_tree/
│   │   │   │   └── fenwick_tree/
│   │   │   ├── visualization/
│   │   │   │   ├── state_builder.py
│   │   │   │   └── models.py            # VisualizationState schema
│   │   │   ├── dryrun/
│   │   │   │   ├── sandbox_runner.py
│   │   │   │   ├── tracer.py
│   │   │   │   └── call_stack_builder.py
│   │   │   └── ai/
│   │   │       ├── base.py              # AIProvider ABC
│   │   │       ├── providers/
│   │   │       │   ├── openai_provider.py
│   │   │       │   └── gemini_provider.py
│   │   │       └── router.py            # failover/selection logic
│   │   ├── repositories/
│   │   │   ├── base_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── algorithm_repository.py
│   │   │   ├── progress_repository.py
│   │   │   ├── chat_repository.py
│   │   │   └── ... (one per collection)
│   │   ├── models/                       # Beanie Documents
│   │   │   ├── user.py
│   │   │   ├── topic.py
│   │   │   ├── algorithm.py
│   │   │   ├── progress.py
│   │   │   ├── bookmark.py
│   │   │   ├── note.py
│   │   │   ├── chat.py
│   │   │   ├── interview_report.py
│   │   │   ├── revision_plan.py
│   │   │   ├── flashcard.py
│   │   │   ├── mind_map.py
│   │   │   ├── achievement.py
│   │   │   ├── history.py
│   │   │   └── analytics_event.py
│   │   ├── schemas/                      # Pydantic DTOs (request/response)
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── algorithm.py
│   │   │   ├── visualization.py
│   │   │   ├── ai.py
│   │   │   └── ...
│   │   ├── prompts/
│   │   │   ├── problem_explainer.py
│   │   │   ├── concept_teacher.py
│   │   │   ├── code_explainer.py
│   │   │   ├── debugger.py
│   │   │   ├── mentor.py
│   │   │   ├── pattern_detector.py
│   │   │   └── solution_comparator.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py               # JWT, password hashing
│   │   │   ├── database.py               # Motor/Beanie init
│   │   │   ├── redis_client.py
│   │   │   └── celery_app.py
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   ├── rate_limit.py
│   │   │   ├── error_handler.py
│   │   │   └── request_id.py
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic-not-used.md   # (Mongo — schema evolution handled via Beanie migrations)
│
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── roadmap/
│   │   │   ├── profile/
│   │   │   ├── bookmarks/
│   │   │   ├── notes/
│   │   │   ├── visualizer/           # X-Ray Mode: 4-panel sync view
│   │   │   ├── dryrun/
│   │   │   ├── ai-mentor/
│   │   │   ├── interview-mode/
│   │   │   ├── contest-mode/
│   │   │   ├── leaderboard/
│   │   │   ├── achievements/
│   │   │   ├── revision-planner/
│   │   │   ├── flashcards/
│   │   │   ├── mindmaps/
│   │   │   └── whiteboard/
│   │   ├── shared/
│   │   │   ├── components/            # shadcn-based design system
│   │   │   ├── hooks/
│   │   │   ├── utils/
│   │   │   └── types/
│   │   ├── layouts/
│   │   ├── routes/
│   │   ├── store/                     # root Zustand store composition
│   │   ├── services/                  # Axios instance, interceptors
│   │   ├── assets/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/workflows/
│   ├── backend-ci.yml
│   ├── frontend-ci.yml
│   └── deploy.yml
└── docs/
    └── (this document set)
```

---

## 6. API Design

Base URL: `/api/v1`. All authenticated routes require `Authorization: Bearer <JWT>`.
AI endpoints support `Accept: text/event-stream` for streaming.

### 6.1 Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Email/password registration |
| POST | `/auth/login` | Email/password login → access + refresh token |
| GET | `/auth/google` | Redirect to Google OAuth consent |
| GET | `/auth/google/callback` | OAuth callback, issues tokens |
| POST | `/auth/refresh` | Rotate refresh token → new access token |
| POST | `/auth/logout` | Revoke refresh token |
| POST | `/auth/verify-email` | Confirm email via token |
| POST | `/auth/forgot-password` | Send reset email |
| POST | `/auth/reset-password` | Reset via one-time token |

### 6.2 Users / Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/users/me` | Current profile |
| PATCH | `/users/me` | Update profile |
| GET | `/dashboard` | Aggregated dashboard payload (streak, heatmap, mastery, recommendation) |

### 6.3 Roadmap / Topics / Algorithms
| Method | Path | Description |
|---|---|---|
| GET | `/topics` | List topics with prerequisite graph |
| GET | `/algorithms` | List/filter algorithms (topic, difficulty, company, pattern) |
| GET | `/algorithms/{slug}` | Algorithm detail (statement, constraints, plugin metadata) |
| GET | `/algorithms/{slug}/companies` | Companies that have asked this problem |

### 6.4 Visualizer / Dry Run
| Method | Path | Description |
|---|---|---|
| POST | `/visualizer/{slug}/run` | Run algorithm plugin with given input → array of `VisualizationState` |
| POST | `/dryrun/execute` | Submit code + input → async job id (sandboxed execution) |
| GET | `/dryrun/jobs/{job_id}` | Poll/SSE job status → trace result |
| GET | `/dryrun/jobs/{job_id}/recursion-tree` | Derived recursion tree from trace |

### 6.5 AI Engine
| Method | Path | Description |
|---|---|---|
| POST | `/ai/explain-problem` | Problem Explainer prompt (streamed) |
| POST | `/ai/teach-concept` | Concept Teacher prompt (streamed) |
| POST | `/ai/explain-code` | Code Explainer prompt (streamed) |
| POST | `/ai/debug` | Debugger prompt — takes code + error/trace (streamed) |
| POST | `/ai/mentor/chat` | Mentor chat turn (streamed, persisted to `chats`) |
| POST | `/ai/detect-pattern` | Pattern Detector — returns structured pattern tags |
| POST | `/ai/compare-solutions` | Solution Comparator — two code blocks → structured comparison |

### 6.6 Progress / Bookmarks / Notes
| Method | Path | Description |
|---|---|---|
| GET/POST | `/progress` | List / upsert progress records |
| GET/POST/DELETE | `/bookmarks` | Manage bookmarks |
| GET/POST/PATCH/DELETE | `/notes` | Manage notes (markdown) |

### 6.7 Interview / Contest / Leaderboard / Achievements
| Method | Path | Description |
|---|---|---|
| POST | `/interview/start` | Begin timed interview session |
| POST | `/interview/{id}/submit` | Submit final code → triggers AI grading job |
| GET | `/interview/{id}/report` | Interview Report (scores, rubric) |
| GET/POST | `/contest` | List contests / register |
| GET | `/leaderboard` | Global/topic/contest leaderboards (paginated) |
| GET | `/achievements` | User's earned + available badges |

### 6.8 Revision / Flashcards / Mind Maps
| Method | Path | Description |
|---|---|---|
| GET/POST | `/revision-plans` | Manage spaced-repetition revision schedule |
| GET/POST/PATCH | `/flashcards` | CRUD + SRS review endpoint (`/flashcards/{id}/review`) |
| GET/POST/PATCH | `/mindmaps` | CRUD for mind map nodes/edges |

### 6.9 Conventions

- All list endpoints support `?page=&limit=&sort=` (cursor-based for high-volume: `history`, `analytics_events`)
- All mutations return the full updated resource (no 204-with-nothing on updates the client needs)
- Errors follow RFC 7807 Problem Details: `{type, title, status, detail, instance}`
- Rate limits: 100 req/min general, 20 req/min for AI endpoints (per user), enforced in `middleware/rate_limit.py` via Redis token bucket

---

## 7. Feature Roadmap

| Release | Features |
|---|---|
| v1.0 (MVP) | Auth, Dashboard, Roadmap, Algorithm Engine (core 10 categories), Visualization Engine, Bookmarks, Notes, Progress |
| v1.1 | Dry Run Engine, Recursion Tree, Memory/Call-Stack views, remaining algorithm categories |
| v1.2 | AI Engine (all 7 prompt types), AI Mentor chat |
| v1.3 | Interview Mode, Pattern Detector integration into problem list |
| v1.4 | Contest Mode, Leaderboards, Achievements |
| v1.5 | Revision Planner, Flashcards (SRS), Mind Maps, Whiteboard |
| v1.6 | Company-wise question banks, Analytics dashboards, polish/perf/accessibility pass |
| v2.0+ (post-launch, out of current scope) | Real-time multiplayer contests, mobile apps, payments |

---

## 8. Development Milestones

Mapped to the client's mandated 7-phase workflow:

| Phase | Milestone | Exit Criteria |
|---|---|---|
| 1 | Architecture (this document) | Approved by stakeholder |
| 2 | Foundation | Auth flows work end-to-end; Dashboard renders with real data; theming/routing complete |
| 3 | Roadmap & Personal Data | Roadmap graph renders; bookmarks/notes/progress CRUD functional |
| 4 | Algorithm + Visualization Engine | ≥3 algorithms per category produce correct `VisualizationState` sequences; X-Ray Mode 4-panel view functional |
| 5 | Dry Run Engine | Sandboxed execution returns accurate trace for recursive + iterative code; recursion tree renders |
| 6 | AI Engine | All 7 prompt types return grounded, schema-valid responses; streaming works; provider failover tested |
| 7 | Interview Mode, Analytics, Deployment | Full interview flow graded; CI/CD green; staging deployment smoke-tested |

---

## 9. Component Hierarchy

Representative hierarchy for the flagship **Algorithm X-Ray Mode** screen (the
most structurally important screen in the product):

```
<XRayModePage>
├── <XRayToolbar>              (play/pause/step/speed/reset, input editor toggle)
├── <XRayLayout>                (resizable 4-pane grid)
│   ├── <CodePane>
│   │   └── <MonacoEditor highlightedLine={state.highlightedLine} />
│   ├── <VisualizationPane>
│   │   └── <VisualizationRenderer state={state} plugin={pluginKey} />
│   │       ├── <ArrayView /> | <TreeView /> | <GraphView /> | <StackView /> | ...
│   │       │     (one renderer per plugin "visualType", all consuming the same
│   │       │      VisualizationState shape — see §15)
│   ├── <MemoryPane>
│   │   ├── <StackFrameList frames={state.callStack} />
│   │   └── <HeapView allocations={state.heap} />
│   └── <ExplanationPane>
│       ├── <AIExplanationStream />   (SSE-driven, keyed to current state index)
│       └── <ComplexityBadge complexity={state.complexity} />
└── <XRayTimeline
      states={states}
      currentIndex={index}
      onScrub={...} />
```

State flow: a single `useVisualizationSession(slug, input)` hook (TanStack Query
+ Zustand slice) owns the `states[]` array and `currentIndex`. All four panes
are pure functions of `states[currentIndex]` — this is what "synchronized"
means architecturally, not four components independently polling.

Top-level route/component map:

```
<App>
├── <AuthLayout>            /login /register /forgot-password
├── <MarketingLayout>       /  (public landing)
└── <AppLayout>             (authenticated shell: sidebar + topbar)
    ├── <DashboardPage>          /app
    ├── <RoadmapPage>            /app/roadmap
    ├── <AlgorithmListPage>      /app/problems
    ├── <AlgorithmDetailPage>    /app/problems/:slug
    ├── <XRayModePage>           /app/problems/:slug/visualize
    ├── <DryRunPage>             /app/problems/:slug/dryrun
    ├── <AIMentorPage>           /app/mentor
    ├── <InterviewModePage>      /app/interview/:sessionId
    ├── <ContestPage>            /app/contest/:id
    ├── <LeaderboardPage>        /app/leaderboard
    ├── <RevisionPlannerPage>    /app/revision
    ├── <FlashcardsPage>         /app/flashcards
    ├── <MindMapsPage>           /app/mindmaps
    ├── <WhiteboardPage>         /app/whiteboard
    ├── <BookmarksPage>          /app/bookmarks
    ├── <NotesPage>              /app/notes
    └── <ProfilePage>            /app/profile
```

---

## 10. Database Schema

Notation: MongoDB collections via Beanie Documents. `ref` = application-level
reference (ObjectId), not a DB-enforced FK.

```python
# users
{
  _id: ObjectId,
  email: str (unique, indexed),
  password_hash: str | None,          # None if OAuth-only
  oauth_provider: "google" | None,
  oauth_id: str | None,
  display_name: str,
  avatar_url: str | None,
  role: "student" | "admin",
  email_verified: bool,
  streak_count: int,
  last_active_at: datetime,
  created_at: datetime,
  updated_at: datetime
}
# indexes: {email: 1} unique, {oauth_provider:1, oauth_id:1}

# topics
{
  _id, name, slug, order: int,
  prerequisite_ids: [ObjectId],       # ref topics
  description: str
}
# indexes: {slug: 1} unique, {order: 1}

# algorithms
{
  _id, slug, title, statement_md, difficulty: "easy"|"medium"|"hard",
  topic_id: ref topics, plugin_key: str,   # maps to engines/algorithms registry
  pattern_tags: [str], companies: [str],
  constraints_md: str, starter_code: {python: str, javascript: str, java: str, cpp: str},
  reference_solution: {...}, time_complexity: str, space_complexity: str,
  created_at, updated_at
}
# indexes: {slug:1} unique, {topic_id:1}, {difficulty:1}, {pattern_tags:1}, {companies:1} (multikey)

# progress
{
  _id, user_id: ref users, algorithm_id: ref algorithms,
  status: "not_started"|"in_progress"|"solved"|"needs_review",
  attempts: int, best_time_ms: int | None,
  hints_used: int, last_attempt_at: datetime, solved_at: datetime | None
}
# indexes: {user_id:1, algorithm_id:1} unique compound, {user_id:1, status:1}

# bookmarks
{ _id, user_id: ref users, algorithm_id: ref algorithms, created_at }
# indexes: {user_id:1, algorithm_id:1} unique compound

# notes
{ _id, user_id: ref users, algorithm_id: ref algorithms, content_md: str, updated_at }
# indexes: {user_id:1, algorithm_id:1}

# chats
{
  _id, user_id: ref users, algorithm_id: ref algorithms | None,
  messages: [{role: "user"|"assistant", content: str, created_at}],
  ai_provider: "openai"|"gemini", created_at, updated_at
}
# indexes: {user_id:1, updated_at:-1}

# interview_reports
{
  _id, user_id: ref users, algorithm_id: ref algorithms,
  transcript: [{role, content, timestamp}], final_code: str,
  scores: {correctness: int, complexity_accuracy: int, communication: int, overall: int},
  duration_ms: int, created_at
}
# indexes: {user_id:1, created_at:-1}

# revision_plans
{ _id, user_id: ref users, scheduled_items: [{algorithm_id, due_at, interval_days}], cadence: str }
# indexes: {user_id:1}, {"scheduled_items.due_at":1}

# flashcards
{ _id, user_id: ref users, algorithm_id: ref algorithms | None, front: str, back: str,
  srs_due_at: datetime, srs_interval_days: int, srs_ease_factor: float }
# indexes: {user_id:1, srs_due_at:1}

# mind_maps
{ _id, user_id: ref users, topic_id: ref topics | None, title: str,
  nodes: [{id, label, x, y}], edges: [{source, target, label}], updated_at }
# indexes: {user_id:1}

# achievements
{ _id, user_id: ref users, badge_key: str, earned_at: datetime }
# indexes: {user_id:1, badge_key:1} unique compound

# history
{ _id, user_id: ref users, algorithm_id: ref algorithms | None, action: str, payload: {}, created_at }
# indexes: {user_id:1, created_at:-1}, TTL index on created_at (180 days)

# analytics_events
{ _id, user_id: ref users | None, event_type: str, metadata: {}, created_at }
# indexes: {event_type:1, created_at:-1}, TTL index (365 days)
```

---

## 11. Deployment Architecture

```
┌───────────────────────────┐        ┌────────────────────────────────┐
│  Vercel (Frontend)         │        │  Render/Railway (Backend)        │
│  - React SPA (static build)│        │  - FastAPI container (N replicas)│
│  - Edge CDN + preview envs │──API──▶│  - Celery worker container(s)    │
│  - Env: VITE_API_BASE_URL  │        │  - Redis (managed add-on)        │
└───────────────────────────┘        │  - NGINX sidecar/ingress          │
                                       └───────────┬───────────────────┘
                                                    │
                                       ┌────────────▼───────────────────┐
                                       │  MongoDB Atlas (managed, M10+)   │
                                       │  - Automated backups             │
                                       │  - VPC peering to backend region │
                                       └──────────────────────────────────┘

CI/CD (GitHub Actions):
  push → backend-ci.yml   (lint: ruff, type-check: mypy, test: pytest, build image)
  push → frontend-ci.yml  (lint: eslint, type-check: tsc, test: vitest, build)
  merge to main → deploy.yml
      1. build + push Docker images (backend) to registry
      2. trigger Render/Railway deploy hook
      3. trigger Vercel production deploy
      4. run post-deploy smoke tests against staging URL
      5. promote to production on green

Local dev: docker-compose.yml spins up api + worker + redis + mongo (local) + frontend (vite dev server), single `docker compose up`.

Environments: local → staging → production, each with isolated MongoDB Atlas
project, Redis instance, and secret sets (managed via GitHub Actions secrets +
Render/Vercel environment variables — never committed).
```

---

## 12. Security Architecture

| Layer | Controls |
|---|---|
| Transport | TLS everywhere (NGINX terminates TLS, HSTS enabled) |
| AuthN | Argon2/bcrypt password hashing, JWT access tokens (short-lived, RS256), refresh tokens rotated + stored hashed in Redis with denylist on logout/breach |
| AuthZ | Role-based (`student`/`admin`) guard dependency in FastAPI (`deps.py::require_role`); resource-level checks (e.g., a note belongs to the requesting user) enforced in `services/`, never trusted from client |
| Input validation | Pydantic schemas on every request boundary; strict types, length limits, enum constraints |
| Code execution sandboxing | Dry Run Engine executes submitted code in an isolated subprocess with: no network namespace, read-only filesystem, CPU time limit (e.g. 5s), memory limit (e.g. 256MB), restricted syscalls (seccomp profile), non-root user, executed inside a disposable container/firecracker-style microVM in production |
| Secrets | Never in source; env vars injected via platform secret managers; AI provider keys scoped server-side only, never exposed to client |
| Rate limiting | Redis token-bucket per user + per IP; stricter limits on `/auth/*` and `/ai/*` |
| CORS | Explicit allow-list of frontend origins per environment |
| Dependency hygiene | GitHub Actions runs `pip-audit`/`npm audit` on CI; Dependabot enabled |
| Data protection | PII minimized in AI prompts (no email/password ever sent to AI providers); MongoDB Atlas encryption at rest; automated backups |
| Auditability | `history`/`analytics_events` collections + structured logs with correlation IDs for traceability |

---

## 13. State Management Strategy

Two distinct kinds of state are deliberately never mixed:

**Server state** (anything that originates from the API: algorithms, progress,
chats, dashboard data) → **TanStack Query**. Query keys are namespaced per
feature (`['algorithms', slug]`, `['progress', userId]`). Mutations use
optimistic updates only where the UX benefit is clear (e.g., bookmarking) and
always roll back on error.

**Client/UI state** (ephemeral, not persisted server-side: current step index
in the visualizer, editor panel layout, modal open/closed, theme) →
**Zustand**, one slice per feature, composed in `store/`. No feature reaches
into another feature's slice directly — cross-feature communication goes
through hooks in `shared/`.

Special case — **Visualization Session state**: the `states[]` timeline
returned by `/visualizer/{slug}/run` is fetched via TanStack Query (it's
server-derived data) but the *current scrub position* is Zustand (it's pure
UI state, changes on every animation frame and must not trigger refetches).
This split is what keeps the 4-panel X-Ray Mode performant — panes subscribe
to a Zustand selector for `currentIndex`, not to the query itself.

Rules:
- No `useState` for anything that outlives a single component's mount, unless truly local (e.g., a form field before submit)
- No server data duplicated into Zustand "just in case"
- All async server interaction goes through `features/<x>/api/` + a matching `hooks/use<X>.ts` wrapper — components never call Axios directly

---

## 14. AI Engine Design

### 14.1 Provider Abstraction

```
engines/ai/base.py        → AIProvider(ABC): .generate(prompt, schema) / .stream(prompt, schema)
engines/ai/providers/
    openai_provider.py    → OpenAIProvider(AIProvider)
    gemini_provider.py    → GeminiProvider(AIProvider)
engines/ai/router.py      → AIRouter: tries primary provider, falls back to
                             secondary on timeout/error/rate-limit, emits a
                             metric on every fallback event for observability
```

Every AI feature is a **prompt template + a Pydantic response schema**, never
a raw string passed to an endpoint. This gives type-safe, validated AI output
that the frontend can render without ad-hoc parsing.

### 14.2 Prompt Template Catalogue

| Template | Input | Output Schema (fields) |
|---|---|---|
| Problem Explainer | algorithm statement, difficulty | `{summary, key_insight, real_world_analogy, approach_outline[]}` |
| Concept Teacher | topic name, user's current mastery level | `{explanation, prerequisites[], common_misconceptions[], practice_suggestions[]}` |
| Code Explainer | user code, language | `{line_by_line[{line, explanation}], overall_summary, complexity{time,space}}` |
| Debugger | user code, error/trace, expected vs actual output | `{root_cause, fix_suggestion, corrected_code_diff, explanation}` |
| Mentor (chat) | conversation history, current algorithm context | streamed free-form text, persisted turn-by-turn to `chats` |
| Pattern Detector | problem statement | `{primary_pattern, secondary_patterns[], confidence, reasoning}` |
| Solution Comparator | two code blocks | `{winner: "a"\|"b"\|"tie", time_complexity_a, time_complexity_b, space_complexity_a, space_complexity_b, tradeoffs, recommendation}` |

### 14.3 Design Principles

- **Grounding over hallucination**: prompts for Code Explainer / Debugger / Pattern Detector are always constructed from the actual `VisualizationState`/trace data where available, not from the code text alone — the AI explains what the Dry Run Engine actually observed, not what it guesses happened.
- **Structured output**: every non-chat template requests strict JSON per its Pydantic schema; `services/ai_service.py` validates and retries once (with a corrective follow-up prompt) on schema-validation failure before surfacing an error.
- **Streaming**: chat and explainer templates stream via SSE for perceived latency; structured-output templates (pattern detector, comparator) are not streamed since the client needs the complete valid object.
- **Cost/latency control**: responses are cached in Redis keyed by `(template, content_hash)` for deterministic templates (Problem Explainer for a given algorithm rarely changes) with a TTL; Mentor chat is never cached (context-dependent).
- **Provider failover**: `AIRouter` is the *only* thing `services/ai_service.py` talks to; provider-specific SDK details never leak past `engines/ai/providers/`.

---

## 15. Visualization Engine Design

### 15.1 Core Contract: `VisualizationState`

The entire "never hardcode animations, generate visualization states" mandate
lives in one schema. Every algorithm plugin's `run()` method returns
`list[VisualizationState]`; every frontend renderer, the Memory Pane, the Call
Stack Pane, and the AI Engine all consume this same list — that shared
contract is what makes the 4 panels of X-Ray Mode "synchronized."

```python
class VisualizationState(BaseModel):
    step_index: int
    highlighted_code_lines: list[int]
    variables: dict[str, Any]              # named locals at this step
    pointers: list[PointerMarker]          # {name, target_index/target_id, color}
    data_structure_snapshot: DataStructureSnapshot
        # a discriminated union: ArraySnapshot | LinkedListSnapshot |
        # TreeSnapshot | GraphSnapshot | StackSnapshot | QueueSnapshot | ...
    call_stack: list[StackFrame]           # {function_name, locals, line}
    heap: list[HeapAllocation]             # {address_id, type, value, refs}
    explanation: str                       # short, human-readable, per-step
    complexity_so_far: ComplexityInfo | None
```

### 15.2 Generation Pipeline

```
AlgorithmPlugin.run(input)
    → yields raw domain events (e.g. "compare(i,j)", "swap(i,j)", "push(stack, val)")
    ↓
engines/visualization/state_builder.py
    → StateBuilder subscribes to domain events, maintains a running snapshot
      of the data structure, and emits one VisualizationState per meaningful
      event (not per line of code — meaningful = something a learner needs
      to see: a comparison, a mutation, a recursive call, a pointer move)
    ↓
list[VisualizationState] persisted transiently (Redis, short TTL) and
returned to the client via /visualizer/{slug}/run
```

This indirection (domain events → StateBuilder → states) is exactly what
prevents animation logic from being hardcoded per-algorithm: a Bubble Sort
plugin and a Merge Sort plugin both just emit `compare`/`swap`/`partition`
events; the *same* `ArraySnapshot` builder renders both, and a new sorting
algorithm plugin gets a working visualization for free by reusing existing
event types, or by defining one new event type consumed by one small
extension to the builder — never by writing new frontend animation code.

### 15.3 Frontend Rendering

`VisualizationRenderer` is a dispatcher keyed by `data_structure_snapshot.type`:

```
type → component
"array"        → <ArrayView/>       (bars/cells, React Flow not needed)
"linked_list"  → <LinkedListView/>  (React Flow nodes/edges)
"tree" | "bst" → <TreeView/>        (React Flow, auto-layout via dagre)
"graph"        → <GraphView/>       (React Flow, force or dagre layout)
"stack"        → <StackView/>
"queue"        → <QueueView/>
"heap"         → <HeapArrayView/>   (array view + implicit tree overlay)
"trie"         → <TrieView/>        (React Flow)
"grid"         → <GridView/>        (for DP tables, backtracking boards)
```

All renderers are pure/presentational: `props: { snapshot, pointers, onNodeHover }`.
None fetches data or knows about the algorithm that produced it — this is
what makes adding algorithm #40 not require touching a single renderer file
if it reuses an existing snapshot type.

---

## 16. Plugin Architecture

### 16.1 Algorithm Plugin Interface

```python
# engines/algorithms/base.py
class AlgorithmPlugin(ABC):
    key: str                    # unique registry key, matches algorithms.plugin_key
    category: AlgorithmCategory # enum: SORTING, SEARCHING, LINKED_LIST, ...
    supported_visualization_types: list[str]

    @abstractmethod
    def default_input(self) -> Any: ...

    @abstractmethod
    def validate_input(self, raw_input: Any) -> Any: ...

    @abstractmethod
    def run(self, input: Any) -> Iterator[DomainEvent]:
        """Yields domain events consumed by the StateBuilder."""

    @abstractmethod
    def complexity(self, input_size: int) -> ComplexityInfo: ...
```

### 16.2 Registration

```python
# engines/algorithms/registry.py
class AlgorithmRegistry:
    _plugins: dict[str, type[AlgorithmPlugin]] = {}

    @classmethod
    def register(cls, plugin_cls: type[AlgorithmPlugin]):
        cls._plugins[plugin_cls.key] = plugin_cls
        return plugin_cls

    @classmethod
    def get(cls, key: str) -> AlgorithmPlugin: ...
```

```python
# engines/algorithms/sorting/bubble_sort.py
@AlgorithmRegistry.register
class BubbleSortPlugin(AlgorithmPlugin):
    key = "bubble-sort"
    category = AlgorithmCategory.SORTING
    supported_visualization_types = ["array"]

    def default_input(self): return {"array": [5, 2, 8, 1, 9]}
    def validate_input(self, raw_input): ...  # bounds/type checks
    def run(self, input):
        arr = input["array"][:]
        for i in range(len(arr)):
            for j in range(len(arr) - i - 1):
                yield CompareEvent(indices=(j, j + 1))
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    yield SwapEvent(indices=(j, j + 1), array_after=arr[:])
    def complexity(self, input_size):
        return ComplexityInfo(time="O(n^2)", space="O(1)")
```

Adding a new algorithm = one new file + `@AlgorithmRegistry.register` +
inserting one `algorithms` document with the matching `plugin_key`. Nothing
in `api/`, `services/`, or the frontend needs to change, provided the
algorithm reuses an existing domain event type — this is the concrete
mechanism behind "Every algorithm should be implemented as a plugin" and
"Never hardcode animations" from the client brief.

### 16.3 AI Prompt Plugin Interface (parallel structure)

```python
# engines/ai/prompts/base.py — mirrors the algorithm plugin pattern
class PromptTemplate(ABC):
    key: str
    response_schema: type[BaseModel]

    @abstractmethod
    def build_prompt(self, context: dict) -> str: ...
```

Each file in `prompts/` implements this once; `services/ai_service.py` looks
templates up by `key` the same way `services/algorithm_service.py` looks up
algorithm plugins by `key` — one consistent extension pattern across both
volatile subsystems, per §2.2.

---

## Approval Checklist

Before Phase 2 (Foundation) code generation begins, please confirm or request
changes to:

- [ ] SRS scope (§1.2) — anything to add/remove from v1?
- [ ] Tech/architecture decisions (§2.2) — any constraint I should account for (e.g., a required cloud provider, an existing auth system to integrate with)?
- [ ] Database schema (§10) — collection shapes acceptable, or do you want SQL/relational instead?
- [ ] API surface (§6) — naming/versioning conventions okay?
- [ ] Plugin interfaces (§16) — signature acceptable as the contract all future algorithm/prompt files will follow?

Once approved, I'll begin **Phase 1 code generation**: repo scaffolding,
`docker-compose.yml`, backend `core/` (config, database, security), and the
base FastAPI app skeleton — then wait for `CONTINUE` before each subsequent
file, per your workflow contract.
