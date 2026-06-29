# SkillBridge — System Architecture

This document is the canonical map of the system as of 2026-05-18. It covers
backend, frontend, the standalone AI script, the AI Engine application that
wraps it, and the mentorship subsystem.

Per-endpoint reference lives in [backend/endpoints.md](backend/endpoints.md);
this document explains *why* things are shaped the way they are.

---

## 1. Overview

SkillBridge is a multi-sided opportunity marketplace connecting **Talents**
(students, bootcamp grads, self-taught), **Organizations** (employers),
**Mentors**, and **Schools** (data trusts). The platform's defining feature
is an **AI Engine** that powers Trust Scores, skill roadmaps, predictive
hiring, mentor matching, mentor session briefs, and curriculum analytics.

There are three deployable surfaces:

| Surface | Tech | Hosts | Talks to |
|---|---|---|---|
| Backend API | Django 5 + DRF + Simple JWT | Gunicorn | Supabase Postgres (ORM), Gemini (AI), Supabase Storage (files) |
| Frontend SPA | React 18 + Vite + Tailwind 4 | Static host | Backend API |
| AI script | Standalone Python | Invoked in-process by backend | Supabase client + Gemini |

The frontend is the **only** client. The AI script is **only** invoked by the
backend's `ai_engine` app — it does not run independently in production.

---

## 2. Repository layout

```
SkillBridge/
├── backend/                    Django project
│   ├── config/                 Settings, root URLConf, ASGI/WSGI
│   ├── core/                   Shared: envelope renderer, exception handler, taxonomy
│   ├── users/                  Custom User model + JWT auth
│   ├── talents/                TalentProfile + TalentSkill + endorsement state
│   ├── mentors/                MentorProfile + endorsements + mentorship subsystem
│   ├── organizations/          Organization + OrganizationMember
│   ├── opportunities/          Opportunity + Application
│   ├── schools/                School + StudentRosterRecord (data-trust)
│   ├── ai_engine/              AI features: trust score, roadmap, matching, ...
│   ├── endpoints.md            Per-endpoint API reference (authoritative)
│   └── requirements.txt
│
├── frontend/                   React SPA
│   └── src/
│       ├── api/                Per-domain fetch wrappers (client.js + auth.js + ...)
│       ├── context/            AuthContext, AIContext
│       ├── hooks/              useApi (generic), useAIInsight (AI-aware)
│       ├── pages/              Route-level screens
│       └── components/         Reusable UI
│
├── ai_script/                  Standalone Gemini CV-matching script
│   └── process_cv_supabase.py
│
└── SYSTEM_ARCHITECTURE.md      This file
```

---

## 3. End-to-end request flow

```
┌─────────────┐        ┌─────────────────────┐        ┌──────────────┐
│  React SPA  │───1───▶│   Django + DRF      │───3───▶│  Supabase PG │
│  (Vite)     │◀──6────│   /api/v1/...       │◀───4───│              │
└─────────────┘        │                     │        └──────────────┘
                       │  ai_engine app      │
                       │  ┌───────────────┐  │        ┌──────────────┐
                       │  │ service layer │──┼───2───▶│  Gemini API  │
                       │  │ + timeout     │◀─┼───5────│              │
                       │  └───────────────┘  │        └──────────────┘
                       └─────────────────────┘

1. Bearer JWT in Authorization header
2. Thread-pool wrapped Gemini call (hard timeout)
3. Django ORM via psycopg2 (uses `postgres` role — bypasses RLS by design)
4. Rows + AIInsight cache
5. JSON response from Gemini (response_mime_type='application/json')
6. Standard envelope: { status, data, meta, errors }
```

---

## 4. Backend

### 4.1 Apps and responsibilities

| App | Owns |
|---|---|
| `config` | Settings, root URLConf, ASGI/WSGI entry points |
| `core` | `StandardJSONRenderer` (envelope wrap), `standard_exception_handler`, `CanonicalSkill`/`CanonicalIndustry` taxonomy |
| `users` | Custom `User` model (email-as-username), Simple JWT signin/signup/refresh, password reset, current-user endpoint |
| `talents` | `TalentProfile`, `TalentSkill`, talent profile + skill CRUD |
| `mentors` | `MentorProfile`, skill endorsements, **mentorship subsystem** (`MentorshipRelationship`, `MentorSession`, `MenteeActivity` + CRUD) |
| `organizations` | `Organization`, `OrganizationMember`, org profile + talent search |
| `opportunities` | `Opportunity`, `Application`, application lifecycle |
| `schools` | `School`, `StudentRosterRecord`, data-trust verification flow |
| `ai_engine` | All AI features, deterministic scoring, caching, signal-based invalidation |

### 4.2 Authentication

- **Custom User**: `users.User` with `email` as login, role flags
  (`is_talent`, `is_mentor`, `is_org_admin`, `is_school_admin`). Configured
  via `AUTH_USER_MODEL = 'users.User'` in [backend/config/settings.py](backend/config/settings.py).
- **JWT issuance**: `rest_framework_simplejwt` with HS256, 1h access /
  7d refresh, signed with `SECRET_KEY`. See `SIMPLE_JWT` block in settings.
- **Flow**:
  1. `POST /auth/signup/` → returns `{user, access_token, refresh_token, expires_in}`
  2. Frontend stores both tokens in `localStorage` ([frontend/src/api/client.js:13](frontend/src/api/client.js#L13))
  3. Every request sends `Authorization: Bearer <access>` ([frontend/src/api/client.js:56](frontend/src/api/client.js#L56))
  4. On `401`, the client silently calls `POST /auth/refresh/` once, retries; on second failure it redirects to `/sign-in`.
- **Why not Supabase Auth**: the project chose Django Simple JWT so the
  auth subject matches `users.User` row IDs (referenced by every FK), with
  no external account-linking concern. Supabase is used only for Postgres
  + Storage.

### 4.3 The standard JSON envelope

Every response — success and error — follows this shape:

```json
{
  "status": "success" | "error",
  "data":   <object|array|null>,
  "meta":   { "pagination": {...}, "http_status": N, ... },
  "errors": [{"field": "...", "message": "...", "code": "..."}]
}
```

Two collaborating components produce it:

| Concern | Component | Location |
|---|---|---|
| Wrap successful responses | `StandardJSONRenderer` | [backend/core/renderers.py](backend/core/renderers.py) |
| Format DRF exceptions consistently | `standard_exception_handler` | [backend/core/exceptions.py](backend/core/exceptions.py) |

Both are wired in the `REST_FRAMEWORK` dict in settings. Views never wrap
manually for success paths — they return raw data and the renderer wraps it.
For error responses with custom error codes (like the AI Engine's
`ai_disabled`), views return the full envelope directly because the renderer
detects pre-wrapped data via `_is_already_wrapped()`.

### 4.4 Error semantics

| HTTP | code (example) | Source |
|---|---|---|
| 400 | `validation_error` | DRF serializer validation, surfaced by exception handler |
| 401 | `not_authenticated` | Simple JWT |
| 403 | `forbidden` / `not_mentor` / `not_owner` | View-level checks |
| 404 | `not_found` | `NotFound`-raising lookups |
| 409 | `conflict` | `core.exceptions.Conflict` (e.g. duplicate mentorship) |
| 502 | `ai_unavailable` | `ai_engine.services.AIServiceError` |
| 503 | `ai_disabled` | `ai_engine.services.AIDisabledError` (missing `GEMINI_API_KEY`) |
| 504 | `ai_timeout` | `ai_engine.services.AITimeoutError` |

The `5xx` AI codes are documented in [backend/endpoints.md](backend/endpoints.md) section 12.

### 4.5 Database

```python
# backend/config/settings.py
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('SUPABASE_DB_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

Django connects to Supabase Postgres directly via the pooler. The connection
uses the `postgres` role which **bypasses RLS** — this is intentional, since
the application enforces authorization in DRF permission classes. If you
later want RLS as defense-in-depth, switch Django to a less-privileged role
and inject `SET request.jwt.claims` per-request — that's a separate piece
of work, not currently implemented.

### 4.6 Data model — key relationships

```
User ──┬── 1 ── TalentProfile ──┬── * ── TalentSkill ── * ── CanonicalSkill
       │                        ├── * ── Application  ── 1 ── Opportunity
       │                        ├── * ── MentorshipRelationship.talent
       │                        └── * ── StudentRosterRecord.talent_profile
       │
       ├── 1 ── MentorProfile ──┬── * ── expertise_areas ── * ── CanonicalSkill
       │                        ├── * ── MentorshipRelationship.mentor
       │                        └── (denorm) endorsements_given
       │
       ├── * ── OrganizationMember ── * ── Organization ── * ── Opportunity
       │
       └── * ── administered_schools ── * ── School ── * ── StudentRosterRecord

MentorshipRelationship ──┬── * ── MentorSession (incl. private_notes)
                         └── * ── MenteeActivity (typed events)

AIInsight  (subject_type, subject_id, kind)  — cache rows, no FKs
```

`StudentRosterRecord.talent_profile` is the join point between a school's
roster and a talent's profile — set when the talent provides consent via
`POST /schools/consent/`.

---

## 5. AI Engine

The `ai_engine` app is structured as a layered cake:

```
views.py         ◀── HTTP, auth, exception → HTTP code mapping
   │
   ▼
services.py      ◀── Pure-Python entry points: takes models, returns dicts
   │                   - get_or_recompute (cache)
   │                   - _call_gemini_with_timeout (LLM)
   │                   - assert_ai_available (key check)
   ▼
scoring.py       ◀── Deterministic Trust Score math, no I/O
   │
   ▼
models.py        ◀── AIInsight cache table
   │
   ▼
signals.py       ◀── post_save handlers that DELETE stale AIInsight rows
```

### 5.1 Three execution patterns

| Endpoint kind | Pattern | Why |
|---|---|---|
| Trust Score, Skill Roadmap, Curriculum Alignment | **Cached** via `AIInsight` (24h TTL), recompute on `?refresh=true` or signal | Read-heavy, expensive to compute |
| Project↔Talent Match, Mentor↔Mentee Match, Predictive Sourcing | **Live** every call | Depend on live pool of opportunities/talents/mentors; org expects fresh |
| Mentee Progress Insight | **Live** every call | Mentor opens it ~2 min before a session; freshness matters |
| Match-CV (legacy) | **Live** every call | User-initiated, payload-dependent (caching by payload hash isn't worth the complexity) |

### 5.2 Caching: `AIInsight` table

Single table for all cached insights:

```python
class AIInsight(models.Model):
    subject_type = CharField   # 'talent' or 'school'
    subject_id = PositiveInt
    kind = CharField           # 'trust_score' | 'skill_roadmap' | 'curriculum_alignment'
    payload = JSONField
    recomputed_at = DateTime(auto_now=True)

    class Meta:
        unique_together = [('subject_type', 'subject_id', 'kind')]
```

Access pattern is always through `services.get_or_recompute(...)` which:
1. Reads existing row, returns it if fresh (`recomputed_at >= now - ttl_hours`)
2. Otherwise calls `recompute_fn()`, upserts the row
3. Returns `(payload, was_recomputed)`

### 5.3 Cache invalidation via signals

Wired in [backend/ai_engine/apps.py](backend/ai_engine/apps.py) `ready()`:

| Source event | Invalidates |
|---|---|
| `post_save` on `TalentSkill` | `trust_score` + `skill_roadmap` for that talent |
| `post_save` on `TalentProfile` | `trust_score` for that talent |
| `post_save` on `StudentRosterRecord` (when `has_consented=True` and linked) | `trust_score` for the linked talent |

Handlers `DELETE` the cache row rather than recomputing eagerly — next read
recomputes naturally and we avoid duplicate work when several fields change
during a single form submit.

### 5.4 Deterministic Trust Score

Computed in [backend/ai_engine/scoring.py](backend/ai_engine/scoring.py).
Four weighted components summing to 100:

| Component | Max | Signal source |
|---|---|---|
| Endorsements | 40 | `TalentSkill.is_endorsed` count, saturates at 5 |
| School verification | 25 | `TalentProfile.is_school_verified` |
| Academic performance | 15 | `StudentRosterRecord.cgpa`, linear scale on 0-5 |
| Profile completeness | 20 | 4 pts each: bio, headline, github/portfolio, linkedin, has-skills |

LLM is used **only for the human-readable `rationale` string** — never for
the number. This is auditable: an employer can recompute the score from raw
data without an API call. If the LLM is down when the score is recomputed,
the score still ships with `rationale: ""` (logged at WARN level).

### 5.5 Graceful degradation

Every LLM-using service function has a fallback path:

| Feature | When LLM fails | Falls back to |
|---|---|---|
| Trust Score rationale | `rationale: ''`, score still returned |
| Skill Roadmap | Deterministic "Learn X — required in N opportunities" list |
| Curriculum Alignment | Deterministic under-representation calc, no narrative |
| Progress Insight | Deterministic activity-type summary |
| Match-CV / Project Match / Mentor Match / Sourcing | 502 (no useful fallback — these ARE the LLM ranking) |

The pattern: the deterministic part runs first and is shipped as `payload`;
the LLM call is wrapped in `try/except AIServiceError` and only enriches
the payload when it succeeds.

### 5.6 `ai_disabled` mode

When `GEMINI_API_KEY` is missing (typical for new local devs):

- `services.assert_ai_available()` raises `AIDisabledError`
- Every AI view catches it via `_handle_ai_exception` → returns `503` with
  `code: "ai_disabled"` and a clear message
- Frontend's [useAIInsight](frontend/src/hooks/useAIInsight.js) detects the
  message text and exposes `aiDisabled: true` so UI can hide AI panels

This lets the rest of the platform be developed locally without anyone
needing a Gemini key.

### 5.7 LLM call mechanics

`_call_gemini_with_timeout` in [backend/ai_engine/services.py](backend/ai_engine/services.py):

```python
with ThreadPoolExecutor(max_workers=1) as pool:
    future = pool.submit(_do_call)
    try:
        raw = future.result(timeout=AI_CALL_TIMEOUT_SECONDS)  # default 30s
    except FuturesTimeoutError:
        raise AITimeoutError(...)
```

The timed-out call's thread keeps running in the background — Python has no
clean way to cancel it. For production at scale this should move to Celery
with `revoke(terminate=True)`. The 30s default is conservative; tune based
on observed Gemini p99.

All LLM responses use `response_mime_type='application/json'` so we get
parseable JSON back; the service layer always parses with `json.loads` and
re-raises as `AIServiceError` on malformed output.

### 5.8 Endpoint catalogue

See [backend/endpoints.md](backend/endpoints.md) section 12 for full specs.
Quick reference:

| Endpoint | Method | Who | Cached? |
|---|---|---|---|
| `/ai/match-cv/` | POST | Any auth | No |
| `/ai/trust-score/me/` | GET | Talent | Yes |
| `/ai/trust-score/talents/<id>/` | GET | Any auth | Yes |
| `/ai/skill-roadmap/me/` | GET | Talent | Yes |
| `/ai/opportunities/<id>/talent-matches/` | GET | Opportunity owner | No |
| `/ai/organizations/<id>/proactive-sourcing/` | GET | Org member | No |
| `/ai/mentor-matches/` | GET | Talent | No |
| `/ai/mentorships/<id>/progress-insight/` | GET | Mentor in relationship | No |
| `/ai/schools/<id>/curriculum-alignment/` | GET | School admin | Yes |

---

## 6. Mentorship subsystem

The `mentors` app owns three new tables (added on `backend` branch, migration
`0002_mentorshiprelationship_mentorsession_menteeactivity`):

| Model | Owns | Notes |
|---|---|---|
| `MentorshipRelationship` | mentor↔talent pairing, status, focus_area | `unique_together=(mentor, talent)`; status: `active`/`paused`/`ended` |
| `MentorSession` | scheduled mentor sessions | `private_notes` is MENTOR-ONLY |
| `MenteeActivity` | typed event log of mentee progress | Either self-logged or system-generated (signals not yet wired) |

### 6.1 Two API surfaces, one data layer

Same database, different views per role — implemented in
[backend/mentors/mentorship_views.py](backend/mentors/mentorship_views.py):

| Mentor sees | Talent sees |
|---|---|
| `/mentors/me/mentorships/` (CRUD) | `/talents/me/mentorships/` (read-only) |
| `/mentors/me/sessions/<id>/` (full CRUD incl. private_notes) | `/talents/me/mentorships/<id>/sessions/` (read, no notes) |
| `/mentors/me/mentorships/<id>/activities/` (read) | `/talents/me/.../activities/` (CRUD own) |

Authorization is enforced by per-relationship helpers
(`_get_mentor_relationship`, `_get_talent_relationship`) that raise `404` if
the row doesn't exist and `403` if the caller is on the wrong side.

The two talent-side serializers — `MentorSessionMentorViewSerializer` vs.
`MentorSessionTalentViewSerializer` — physically omit `private_notes` from
the talent payload so it cannot leak even if a view picks the wrong one.

### 6.2 Lifecycle conventions

- **Creation**: Mentor adds a talent unilaterally (`POST /mentors/me/mentorships/`).
  There is no PENDING/ACCEPT flow yet; that's a deliberate MVP simplification.
- **Ending**: `PATCH` with `status: "ended"` stamps `ended_at` automatically.
  No hard delete — relationships preserve history for past-hire analytics.
- **Sessions**: Mentor schedules, sets `private_notes` post-session. The
  `status` lifecycle is `scheduled → completed | cancelled | no_show`.
- **Activities**: Talent self-logs (`project_shipped`, `blocker_reported`,
  etc.). Future system-generated rows (when a `TalentSkill` is endorsed)
  are not yet wired — see "Known limitations".

### 6.3 Endpoint catalogue

See [backend/endpoints.md](backend/endpoints.md) section 11. Quick reference:

| Endpoint | Methods | Who |
|---|---|---|
| `/mentors/me/mentorships/` | GET, POST | Mentor |
| `/mentors/me/mentorships/<id>/` | GET, PATCH | Mentor in relationship |
| `/mentors/me/mentorships/<id>/sessions/` | GET, POST | Mentor |
| `/mentors/me/sessions/<id>/` | GET, PATCH, DELETE | Mentor |
| `/mentors/me/mentorships/<id>/activities/` | GET | Mentor |
| `/talents/me/mentorships/` | GET | Talent |
| `/talents/me/mentorships/<id>/` | GET | Talent |
| `/talents/me/mentorships/<id>/sessions/` | GET | Talent (no notes) |
| `/talents/me/mentorships/<id>/activities/` | GET, POST | Talent |
| `/talents/me/activities/<id>/` | PATCH, DELETE | Talent |

---

## 7. Frontend

### 7.1 Layout

```
frontend/src/
├── api/
│   ├── client.js         Base fetch wrapper. Adds Authorization header,
│   │                     silently refreshes expired JWTs, unwraps envelope.
│   ├── auth.js           signin / signup / signout / me
│   ├── opportunities.js  list / get / apply / mine
│   ├── talents.js        profile + skills
│   ├── organizations.js
│   └── ai.js             All AI Engine calls
├── context/
│   ├── AuthContext.jsx   Holds user + login/logout/refreshUser
│   └── AIContext.jsx     Holds match-cv (one-off CV match) state
├── hooks/
│   ├── useApi.js         Generic: { data, loading, error, refetch }
│   └── useAIInsight.js   AI-aware: adds `refresh()` + `aiDisabled`
├── pages/                One per route
└── components/           UI primitives (Button, PageHeader, etc.)
```

### 7.2 The fetch wrapper

[frontend/src/api/client.js](frontend/src/api/client.js) is the only place
that knows about JWTs and the envelope.

- Adds `Authorization: Bearer <token>` from `localStorage`
- On `401`: tries `POST /auth/refresh/` once, retries the original request;
  on second failure, clears tokens and redirects to `/sign-in`
- On envelope `status: "error"` or non-2xx: throws `Error(message)` with
  the first error's message
- On success: returns `json.data` (envelope-unwrapped)

This means every page-level `api.foo()` call returns the inner payload
directly — no `.data.data` patterns.

### 7.3 Hooks

- **`useApi(apiFn, deps)`** — generic. Runs on mount + deps change, exposes
  `{ data, loading, error, refetch }`. Used widely (e.g. [ApplyPage.jsx:11](frontend/src/pages/ApplyPage.jsx#L11)).
- **`useAIInsight(apiFn, deps)`** — adds:
  - `refresh()` that calls `apiFn({ refresh: true })` to hit `?refresh=true`
  - `aiDisabled` flag derived from the 503 error message
  - In-flight `AbortController` for unmount/cancel semantics
  - Use when consuming any AI Engine endpoint.

### 7.4 Contexts

- **`AuthProvider`** — wraps the whole app. Holds `user`, role flags,
  `login` / `register` / `logout` / `refreshUser`. Tokens are persisted in
  `localStorage`, restored on app boot via `GET /auth/me/`.
- **`AIProvider`** — currently holds state for the `match-cv` operation
  only. Newer AI calls go through `useAIInsight` instead (no provider
  needed; cached on backend).

Both are wired in [frontend/src/main.jsx](frontend/src/main.jsx):

```jsx
<AuthProvider>
  <AIProvider>
    <App />
  </AIProvider>
</AuthProvider>
```

---

## 8. The standalone AI script

[ai_script/process_cv_supabase.py](ai_script/process_cv_supabase.py) is a
single-function module:

```python
def process_cv_comparison(cv_data: dict) -> list:
    # 1. Fetch uncompared rows from Supabase `company_requirements`
    # 2. For each: prompt Gemini (CV vs. requirement) → JSON {is_match, reason}
    # 3. Mark row `is_compared=True` regardless of outcome
    # 4. Return list of matching requirement IDs
```

It uses the `supabase-py` client (with `SUPABASE_URL` + `SUPABASE_KEY`
service-role) and the `google-genai` SDK directly — neither goes through
Django.

**Integration**: `ai_engine.services.match_cv_against_requirements()` adds
`ai_script/` to `sys.path` lazily, imports the function, and runs it inside
the same `ThreadPoolExecutor` timeout pattern used for other Gemini calls.
The script is left untouched so it remains runnable standalone for the AI
team.

---

## 9. Environment variables

Place in `backend/.env`. Loaded automatically by `python-dotenv` in
[backend/config/settings.py:17](backend/config/settings.py#L17).

| Var | Required? | Default | Used by |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Yes (in prod) | unsafe placeholder | Django + JWT signing key |
| `DEBUG` | No | `True` | Django |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Django |
| `SUPABASE_DB_URL` | Yes | falls back to SQLite | Database |
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:3000,...` | django-cors-headers |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_STORAGE_BUCKET_NAME` / `AWS_S3_ENDPOINT_URL` | Optional | — | Supabase Storage (S3-compatible) |
| `GEMINI_API_KEY` | Optional (AI features 503 without it) | — | AI Engine |
| `SUPABASE_URL` / `SUPABASE_KEY` | Optional (match-cv 503 without them) | — | AI script |
| `AI_CALL_TIMEOUT_SECONDS` | No | `30` | AI Engine call timeout |
| `AI_GEMINI_MODEL` | No | `gemini-3-flash-preview` | AI Engine model selection |

---

## 10. Local setup

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

```powershell
# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` (Vite default) or `http://localhost:3000`
depending on `vite.config.js`. The backend should be reachable at
`http://localhost:8000/api/v1/`.

### Quick auth check

```bash
curl -X POST http://localhost:8000/api/v1/auth/signin/ \
  -H "Content-Type: application/json" \
  -d '{"email": "talent@skillbridge.com", "password": "TestPassword123!"}'
```

(Test accounts seeded by `python manage.py seed_data` — see
[backend/endpoints.md](backend/endpoints.md) bottom of file.)

---

## 11. Production checklist

- [ ] Set `DEBUG=False` and a real `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- [ ] Set `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` so AI endpoints don't 503
- [ ] Run `python manage.py collectstatic`
- [ ] Run behind Gunicorn (already in `requirements.txt`):
      `gunicorn config.wsgi --workers 3 --timeout 60`
- [ ] Verify `AI_CALL_TIMEOUT_SECONDS` < Gunicorn `--timeout`, or hung Gemini calls will kill workers
- [ ] Decide on RLS strategy (currently bypassed via `postgres` role — see §4.5)
- [ ] Decide when to migrate sync AI calls to Celery (see §5.7)

---

## 12. Known limitations / next chunks of work

### AI Engine

- **Thread-pool timeout cannot cancel hung Gemini calls.** They keep
  running in the background until the SDK gives up. For high traffic, move
  to Celery with `terminate=True` revocation.
- **Frontend detects `ai_disabled` by message regex.** The envelope's
  `errors[0].code` is the right field to read but `client.js` throws plain
  `Error` objects with only `.message`. Fix: enrich `client.js` to attach
  `err.code` and `err.status`.
- **Predictive Sourcing is honest about low confidence** but does not yet
  weight "high-performing" hires (no post-hire performance signal exists).
- **Project↔Talent and Mentor↔Mentee matches are NOT cached.** If org/
  talent dashboards start hitting these on every page load, add a short-TTL
  cache (5-15 min) per (subject, query) pair.

### Mentorship

- **No request/accept flow.** Mentor unilaterally adds a talent. Adding a
  `PENDING` status + talent-side accept endpoint is ~30 LOC if needed.
- **System-generated `MenteeActivity` rows are not wired.** When a mentor
  endorses a skill (a `TalentSkill` `is_endorsed → True` event), no
  `skill_endorsed` activity row is created. A `post_save` handler in
  `mentors/signals.py` would do this — held back because it requires a
  product decision on which events should auto-log.
- **Mentor cannot read mentee's other activity** (e.g. activities logged
  under a different relationship). By design — each relationship is its own
  scope.

### Supabase

- **RLS is bypassed.** See §4.5. Authorization is purely DRF permission
  classes today. Defense-in-depth via RLS is a separate hardening pass.
- **Two data paths exist**: Django ORM (relational tables) and `supabase-py`
  (only in the AI script, only for `company_requirements`). If you ever
  start touching `company_requirements` from Django, move it to a model so
  the two paths don't diverge.

### Frontend

- **`AuthContext` does not handle JWT refresh failures gracefully across
  tabs.** A 401-driven redirect happens in `client.js`; multi-tab sync via
  `storage` events isn't implemented.

---

## 13. Where to add things

| Want to add... | Touch this |
|---|---|
| New API endpoint in an existing app | `<app>/views.py`, `<app>/serializers.py`, `<app>/urls.py`, append to `endpoints.md` |
| New AI feature | `ai_engine/services.py` (service fn), `ai_engine/views.py` (view), `ai_engine/urls.py` (route), `frontend/src/api/ai.js` (call), `endpoints.md` |
| New cached AI insight kind | Add `KIND_*` to `ai_engine/models.py:AIInsight`, write a service fn that calls `get_or_recompute(kind=...)`, add invalidation handler in `ai_engine/signals.py` |
| New domain (e.g. "Reviews") | New Django app under `backend/`, register in `INSTALLED_APPS` + `config/urls.py`, write models/views/serializers/urls, append to `endpoints.md` |
| New frontend API surface | New `frontend/src/api/<domain>.js` calling `apiRequest`, optionally a hook in `hooks/`, consume from pages |
| Background invalidation of a cached insight | `post_save` handler in `ai_engine/signals.py`, connect in `apps.py:ready()` |

---

*Last updated: 2026-05-18.*
