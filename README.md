# TrustPulse

TrustPulse is a personal-scale version of "continuous authentication" — the same
design pattern used by enterprise security tools like Citrix Adaptive Auth and
Beyond Identity, but built for an individual, not a company. Instead of checking
identity once at login and checking a website once when visiting it, TrustPulse
fuses both into **one continuously updating Trust Score (0-100)** for the whole
session, and reacts proportionally: no friction when trust is high, a
plain-language warning when it dips, and a re-verification requirement only if
the drop is sustained or severe.

## What's simulated vs. real

- **Identity is simulated.** Enrollment issues a synthetic "demo card"
  (`DC` + 4 digits) generated entirely by this app. There is **no real
  Aadhaar/UIDAI integration** — individuals don't have access to a public
  UIDAI verification API, so this project models the same trust-scoring
  pattern with a self-issued identity credential instead.
- **Face matching is real, but fully local.** Face detection (MediaPipe),
  embeddings (a pretrained FaceNet model via facenet-pytorch, vggface2
  weights), liveness checks, and cosine-similarity matching all run on the
  local FastAPI backend. No image or embedding is ever sent to a cloud API —
  this is a core design principle, not a shortcut, and is enforced by the
  code never making an outbound call for face processing.
- **Site risk checks are real, local heuristics.** SSL validity is checked
  directly via Python's `ssl`/`socket` modules (no external API), and
  lookalike-domain scoring is a local Levenshtein-distance comparison against
  a small hardcoded brand list.

## Trust score formula

```
trust_score = 0.4 * identity_confidence
            + 0.3 * (100 - site_risk)
            + 0.2 * behavior_score
            + 0.1 * environment_score
```

- `identity_confidence`: latest face-match score for the session's card, scaled to 0-100.
- `site_risk`: latest risk score (0-100, higher = riskier) from the most recent URL check.
- `behavior_score`: 100 while active, linearly decaying to 0 as idle time approaches 60 seconds.
- `environment_score`: hardcoded to 100 in this build (see Limitations below).

Escalation:
- `trust_score < 60` → `flag: "warning"`
- `trust_score < 60` sustained for more than 15 seconds, or `trust_score < 35` immediately → `flag: "reverify"`
- otherwise → `flag: "none"`

Every recalculation writes a row to `trust_events` with a `reason_code`
(e.g. `lookalike_domain`, `ssl_invalid`, `idle_timeout`, `low_match_score`),
which the dashboard turns into a plain-language sentence via the backend's
explainability module.

## How to run

Two terminals, run independently:

**Backend**
```
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Dashboard**
```
cd dashboard
npm install
npm run dev
```

The dashboard expects the backend at `http://localhost:8000` and is served at
`http://localhost:5173` (CORS is pre-configured for this origin).

## Limitations & future work

- `environment_score` is a hardcoded placeholder (always 100) — a real build
  would fold in signals like new-device detection, IP/geolocation shifts, or
  browser fingerprint changes.
- There's no re-enrollment flow if a user's face changes significantly over
  time (facial hair, aging, injury) — the only remedy today is enrolling a new card.
- No multi-user/shared-device detection — the system assumes one enrolled
  identity per session and doesn't detect a handoff to a second person.
- A browser extension was explicitly scoped out of this build in favor of the
  React dashboard, but it's the natural next step for production use — a real
  deployment would want continuous signals from the browser itself (tab
  focus, navigation events, keystroke/mouse cadence) rather than a
  dashboard the user has to keep open.
