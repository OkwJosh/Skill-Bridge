# SkillBridge — React Frontend (Backend Connected)

React + Vite + Tailwind CSS frontend fully wired to the Django/Supabase backend.

---

## Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Start the backend first
Make sure your Django backend is running at `http://localhost:8000`

### 3. Fix CORS (⚠️ important)
In the backend `.env`, add port 5173 to CORS:
```
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```
Then restart the backend.

### 4. Start the frontend
```bash
npm run dev
```

Open **http://localhost:5173**

### 5. Log in with a test account
| Email | Password | Role |
|-------|----------|------|
| talent@skillbridge.com | TestPassword123! | Talent |
| orgadmin@skillbridge.com | TestPassword123! | Org Admin |
| mentor@skillbridge.com | TestPassword123! | Mentor |

---

## Project Structure

```
src/
├── api/
│   ├── client.js          ← Base fetcher (auth headers, token refresh, error handling)
│   ├── auth.js            ← signin, signup, signout, getMe, updateMe
│   ├── opportunities.js   ← getOpportunities, getOpportunity, applyToOpportunity
│   ├── talents.js         ← getMyTalentProfile, updateMyTalentProfile, addSkill
│   └── organizations.js   ← getMyOrganization, searchTalent
├── context/
│   └── AuthContext.jsx    ← login, logout, register, user state (wraps whole app)
├── hooks/
│   └── useApi.js          ← useApi(fn, deps) — data fetching with loading/error state
├── components/
│   ├── AppLayout.jsx      ← Sidebar nav (shows real user name from API)
│   └── UI.jsx             ← Button, Input, JobCard, Badge, Avatar, etc.
├── data/
│   └── index.js           ← Dummy data (categories, fallback talent profiles)
├── pages/                 ← All 19 pages
└── App.jsx                ← Routes + ProtectedRoute guard
```

---

## How Authentication Works

1. User logs in → backend returns `access_token` + `refresh_token`
2. Tokens are saved to `localStorage`
3. Every API request sends `Authorization: Bearer <access_token>`
4. If the token expires (401), `client.js` automatically tries to refresh it
5. If refresh fails, user is redirected to `/sign-in`
6. `ProtectedRoute` in `App.jsx` prevents access to `/app/*` pages when not logged in

---

## Backend API Base URL

The base URL is set in `src/api/client.js`:
```js
const BASE_URL = 'http://localhost:8000/api/v1';
```
Change this when deploying to production.

---

## Pages & Their Data Source

| Page | API Endpoint |
|------|-------------|
| Sign In | POST `/auth/signin/` |
| Create Account | POST `/auth/signup/` |
| Home | GET `/opportunities/` |
| Jobs | GET `/opportunities/?search=...&opportunity_type=...` |
| Job Details | GET `/opportunities/:id/` |
| Apply | POST `/opportunities/:id/apply/` |
| Notifications | GET `/opportunities/my-applications/` |
| Profile | GET + PATCH `/auth/me/` |
| Talent (org admin) | GET `/organizations/me/talent-search/` |
| Settings | Logout via POST `/auth/signout/` |
