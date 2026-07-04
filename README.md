# TrustPulse

TrustPulse is a continuous authentication platform: instead of checking
identity once at login, it fuses identity, site-risk, and behavior signals
into **one continuously updating Trust Score (0-100)** for the whole session,
and reacts proportionally — no friction when trust is high, a plain-language
warning when it dips, and a re-verification requirement only if the drop is
sustained or severe.

The platform is one API with two independent clients:

```
backend/     FastAPI + async SQLAlchemy 2.0 (asyncpg) + PostgreSQL (Neon)
dashboard/   React/Vite admin reporting UI + consumer demo login
extension/   Manifest V3 Chrome extension — the primary continuous-auth client
```

Both clients talk to the same backend over HTTP; neither has its own copy of
the trust-scoring logic.

## What's simulated vs. real

- **Identity is simulated.** Enrollment issues a synthetic "demo card"
  (`DC` + 4 digits) generated entirely by this app. There is no real
  government ID integration.
- **Face matching is real, but fully local.** Face detection (MediaPipe),
  embeddings (a pretrained FaceNet model via facenet-pytorch, vggface2
  weights), liveness checks, and cosine-similarity matching all run on the
  local FastAPI backend. No image or embedding is ever sent to a cloud API.
- **Site risk checks are real, local heuristics.** SSL validity is checked
  directly via Python's `ssl`/`socket` modules, and lookalike-domain scoring
  is a local Levenshtein-distance comparison against a small hardcoded brand
  list.

## Trust score formula

```
trust_score = 0.4 * identity_confidence
            + 0.3 * (100 - site_risk)
            + 0.2 * behavior_score
            + 0.1 * environment_score
```

This formula, its weights, and its thresholds (`IDLE_MAX_SECONDS=60`,
`WARNING_THRESHOLD=60`, `REVERIFY_IMMEDIATE_THRESHOLD=35`) live in
[`backend/app/modules/trust/trust_engine.py`](backend/app/modules/trust/trust_engine.py)
and are the one piece of business logic every client defers to — the
dashboard and extension only ever display scores the backend computed, never
recompute them.

Escalation:
- `trust_score < 60` → `flag: "warning"`
- `trust_score < 60` sustained for more than 15 seconds, or `trust_score < 35`
  immediately → `flag: "reverify"`
- otherwise → `flag: "none"`

Every recalculation writes a row to `trust_events` with a `reason_code`
(e.g. `lookalike_domain`, `ssl_invalid`, `idle_timeout`, `low_match_score`),
which is turned into a plain-language sentence by
[`trust/explain.py`](backend/app/modules/trust/explain.py) — clients only
ever render text the backend returns.

## Architecture

### Backend (`backend/app/`)

- `modules/` — one package per bounded context (`enroll`, `verify`, `trust`,
  `session`, `risk`, `dashboard`, `auth`), each with `routes.py` →
  `handlers.py` → `services.py` → `repository.py` (+ `schemas.py`). Routes do
  HTTP glue only; services hold business logic; repositories are the only
  layer that touches the database.
- `shared/` — cross-cutting code: the unchanged face pipeline
  (`face_detect.py`, `embedding.py`, `liveness.py`, `matcher.py`), the async
  DB engine/session (`database.py`, `models.py`), JWT + password hashing
  (`security.py`), rate limiting (`rate_limit.py`), structured JSON logging
  (`logging.py`), and the exception → HTTP response mapping
  (`exceptions.py`).
- Every response is `{success, data, error}`. `/enroll`, `/verify`,
  `/session/*`, and `/risk-check` are public but rate-limited (10/min by
  default). `/dashboard/*` and `/trust/*` require an admin JWT, issued via
  `/auth/login` and delivered as an httpOnly cookie.
- Database access is async SQLAlchemy 2.0 over `asyncpg`, targeting an
  existing Neon Postgres database. Alembic manages future schema changes;
  the initial revision was generated against the already-existing tables and
  stamped (not applied) so it doesn't try to recreate them.

### Dashboard (`dashboard/src/`)

- `api/` — one file per backend module (`authApi.js`, `enrollApi.js`,
  `verifyApi.js`, `sessionApi.js`, `riskApi.js`, `trustApi.js`,
  `dashboardApi.js`), all built on a shared `client.js` that sends
  `credentials: 'include'` so the admin cookie is attached automatically.
- Two independent flows in one app: a **consumer demo** (`/login`,
  `/enroll`, `/bank`) that verifies a face against a card and starts a
  session, and an **admin reporting area** (`/reports`, `/reports/:cardId`)
  gated behind `/admin/login` and a `RequireAdmin` route guard. `/site-risk`
  is public, matching the backend's public `/risk-check` endpoint.
- A global `ErrorBoundary` and a toast layer (`toast.js` +
  `ToastContainer.jsx`) surface unexpected errors and failed API calls.

### Extension (`extension/`)

Manifest V3, and the intended primary client for continuous auth — it runs
in the background rather than requiring a dashboard tab to stay open.

- `background/service-worker.js` — owns session state in
  `chrome.storage.local`, runs a `chrome.alarms`-driven heartbeat loop
  against `/session/heartbeat`, and triggers re-verification when the
  backend flags `reverify`.
- `offscreen/` — an Offscreen Document that captures a webcam frame for
  periodic re-verification without a popup open. The camera indicator will
  be visibly active during these checks — that's expected, not a bug.
  Offscreen documents can't show a permission prompt themselves; they only
  work once the extension has already been granted camera access from a
  real page (see `capture/` below).
- `capture/` — a dedicated window (opened via `chrome.windows.create`, not
  the action popup) that hosts the actual login/enroll camera UI. This is
  deliberate: the action popup is a transient surface, and Chrome
  auto-dismisses the getUserMedia permission prompt (`NotAllowedError:
  Permission dismissed`) if the popup loses focus while it's showing — which
  it reliably does. A real window doesn't have that problem.
- `content-scripts/site-monitor.js` — registered dynamically (via
  `chrome.scripting`) only for sites added under Options → Protected Sites,
  never on `<all_urls>`. It reports the current URL to the background
  worker, which calls `/risk-check`.
- `popup/` — a lightweight launcher: session status, the live trust score
  badge (green ≥60, amber 35-59, red <35 — the same thresholds as the
  backend), and buttons that open the `capture/` window. It holds no camera
  code itself.
- `options/` — re-verify interval, protected sites list, and session
  revocation.

## How to run

Three independent pieces:

**Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in DATABASE_URL, JWT_SECRET, ADMIN_EMAIL/PASSWORD
python scripts/seed_admin.py   # hashes ADMIN_PASSWORD into ADMIN_PASSWORD_HASH, then remove ADMIN_PASSWORD
alembic upgrade head   # only needed on a fresh database with no tables yet
uvicorn app.main:app --reload
```
`GET /health` does a real `SELECT 1` against Neon — check it after boot.

**Dashboard**
```
cd dashboard
npm install
npm run dev
```
Visit `http://localhost:5173`. Admin routes (`/reports`) redirect to
`/admin/login` until you sign in with the seeded admin account.

**Extension**
```
cd extension
npm run build   # writes src/config.js from .env (defaults to localhost:8000)
```
Then in Chrome: `chrome://extensions` → Developer mode → Load unpacked →
select the `extension/` folder.

## Limitations & future work

- `environment_score` is a hardcoded placeholder (always 100) — a real build
  would fold in signals like new-device detection, IP/geolocation shifts, or
  browser fingerprint changes.
- There's no re-enrollment flow if a user's face changes significantly over
  time — the only remedy today is enrolling a new card.
- No multi-user/shared-device detection — the system assumes one enrolled
  identity per session.
- The admin account is a single set of credentials from environment
  variables, not a full user-management system.
