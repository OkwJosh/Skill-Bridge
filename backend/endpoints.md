# SkillBridge API Documentation

> **Base URL:** `http://localhost:8000/api/v1`  
> **Auth Header:** `Authorization: Bearer <supabase_access_token>`  
> **Response Format:** All responses use the standard envelope

```json
{
  "status": "success" | "error",
  "data": { ... },
  "meta": { ... },
  "errors": []
}
```

---

## 📋 Table of Contents

1. [Authentication](#1-authentication)
2. [User Profile](#2-user-profile)
3. [Talent Profiles](#3-talent-profiles)
4. [Talent Skills](#4-talent-skills)
5. [Organizations](#5-organizations)
6. [Mentors](#6-mentors)
7. [Opportunities](#7-opportunities)
8. [Applications](#8-applications)
9. [Schools & Verification](#9-schools--verification)
10. [Taxonomy (Skills/Industries)](#10-taxonomy)

---

## 1. Authentication

### POST `/auth/signup/`
**Register a new user**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone_number": "+2348012345678",
  "role": "talent"
}
```

| Field | Type | Required | Options |
|-------|------|----------|---------|
| `email` | string | ✅ | Valid email |
| `password` | string | ✅ | Min 6 chars |
| `full_name` | string | ❌ | Max 255 chars |
| `phone_number` | string | ❌ | With country code |
| `role` | string | ❌ | `talent`, `org_admin`, `mentor`, `school_admin` |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "user": { "id": 1, "email": "user@example.com", "roles": ["talent"], ... },
    "access_token": "eyJhbG...",
    "refresh_token": "v1.MRj...",
    "expires_in": 3600,
    "token_type": "bearer"
  }
}
```

---

### POST `/auth/signin/`
**Login with email and password**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user": { "id": 1, "email": "...", "roles": ["talent"], ... },
    "access_token": "eyJhbG...",
    "refresh_token": "v1.MRj...",
    "expires_in": 3600
  }
}
```

---

### POST `/auth/signout/`
**Logout current user**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Any |

**Response (200):**
```json
{
  "status": "success",
  "data": { "message": "Successfully signed out" }
}
```

---

### POST `/auth/refresh/`
**Refresh expired access token**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:**
```json
{
  "refresh_token": "v1.MRjWK..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "v1.NEW...",
    "expires_in": 3600
  }
}
```

---

### POST `/auth/password/reset/`
**Request password reset email**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:** `{"email": "user@example.com"}`

Always returns 200 regardless of whether the email is registered
(anti-enumeration). The email body contains a link to `FRONTEND_URL/reset-password?uid=…&token=…`.

**Response (200):**
```json
{
  "status": "success",
  "data": { "message": "If an account with this email exists, a password reset link has been sent." }
}
```

---

### POST `/auth/password/confirm/`
**Set new password using uid + token from the reset link**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:**
```json
{
  "uid": "<base64 from email link>",
  "token": "<token from email link>",
  "new_password": "NewSecurePass123!"
}
```

**Errors:**
| HTTP | Code | When |
|---|---|---|
| 400 | bad_request | uid/token invalid or expired, or `new_password` < 6 chars |

---

### POST `/auth/google/`
**Sign in with Google (OAuth ID token)**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

The frontend obtains an ID token via Google Identity Services and POSTs it
here. The backend validates the signature + audience against `GOOGLE_OAUTH_CLIENT_ID`,
finds or creates the user, and issues a JWT pair.

**Request Body:** `{"id_token": "<google id token>"}`

**Response (200):** same shape as `/auth/signin/` — `{user, access_token, refresh_token}`.
The returned user will have `needs_onboarding: true` on first OAuth signup.

**Errors:**
| HTTP | Code | When |
|---|---|---|
| 401 | oauth_invalid_token | Token signature/expiry/audience failed verification |
| 503 | oauth_disabled | `GOOGLE_OAUTH_CLIENT_ID` is not set on the server |

---

### POST `/auth/apple/`
**Sign in with Apple (OAuth ID token)**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

Same shape as `/auth/google/`. Backend validates against `APPLE_SERVICE_ID`
and Apple's JWKS at `https://appleid.apple.com/auth/keys`.

**Note:** Apple omits `email` on subsequent sign-ins after the first. The
backend re-identifies users via `(provider='apple', subject)` stored in
`OAuthIdentity`, so this works transparently.

**Request Body:** `{"id_token": "<apple id token>"}`

**Errors:** same codes as `/auth/google/` (`oauth_invalid_token`, `oauth_disabled`).

---

## 2. User Profile

### GET `/auth/me/`
**Get current user's profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Any |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone_number": "+2348012345678",
    "avatar_url": "",
    "roles": ["talent", "mentor"],
    "is_talent": true,
    "is_org_admin": false,
    "is_mentor": true,
    "is_school_admin": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### PATCH `/auth/me/`
**Update current user's profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Any |

**Request Body:**
```json
{
  "full_name": "John Updated",
  "phone_number": "+2349012345678",
  "avatar_url": "https://storage.supabase.com/...",
  "is_talent": true,
  "is_mentor": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `full_name` | string | Display name |
| `phone_number` | string | Phone with country code |
| `avatar_url` | string | Profile photo URL |
| `is_talent` | boolean | Enable talent role |
| `is_org_admin` | boolean | Enable org admin role |
| `is_mentor` | boolean | Enable mentor role |

---

## 3. Talent Profiles

### GET `/talents/me/`
**Get current user's talent profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user": { "id": 1, "email": "...", "full_name": "..." },
    "headline": "Full Stack Developer | React & Django",
    "bio": "Passionate developer...",
    "education_route": "university",
    "institution_name": "University of Lagos",
    "field_of_study": "Computer Science",
    "graduation_year": 2024,
    "city": "Lagos",
    "state": "Lagos State",
    "country": "Nigeria",
    "is_available": true,
    "is_school_verified": false,
    "portfolio_url": "https://johndoe.dev",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "github_url": "https://github.com/johndoe",
    "skills": [
      { "skill": { "id": 1, "name": "Python" }, "proficiency": "advanced", "years_experience": 3, "is_primary": true, "is_endorsed": false }
    ]
  }
}
```

---

### PATCH `/talents/me/`
**Update talent profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Request Body:**
```json
{
  "headline": "Senior Full Stack Developer",
  "bio": "5 years of experience building web applications...",
  "education_route": "university",
  "institution_name": "University of Lagos",
  "field_of_study": "Computer Science",
  "graduation_year": 2024,
  "city": "Lagos",
  "state": "Lagos State",
  "is_available": true,
  "portfolio_url": "https://johndoe.dev",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe"
}
```

| Field | Type | Options |
|-------|------|---------|
| `education_route` | string | `university`, `polytechnic`, `bootcamp`, `self_taught` |
| `is_available` | boolean | Looking for opportunities |

---

## 4. Talent Skills

### POST `/talents/me/skills/`
**Add a skill to profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Request Body:**
```json
{
  "skill_id": 1,
  "proficiency": "intermediate",
  "years_experience": 2,
  "is_primary": false
}
```

| Field | Type | Required | Options |
|-------|------|----------|---------|
| `skill_id` | integer | ✅ | ID from CanonicalSkill |
| `proficiency` | string | ❌ | `beginner`, `intermediate`, `advanced`, `expert` |
| `years_experience` | integer | ❌ | 0+ |
| `is_primary` | boolean | ❌ | Highlight on profile |

---

### PATCH `/talents/me/skills/<skill_id>/`
**Update skill details**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Request Body:**
```json
{
  "proficiency": "advanced",
  "years_experience": 4,
  "is_primary": true
}
```

---

### DELETE `/talents/me/skills/<skill_id>/`
**Remove skill from profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Response (200):**
```json
{
  "status": "success",
  "data": null,
  "meta": { "message": "Skill removed from profile." }
}
```

---

## 5. Organizations

### GET `/organizations/me/`
**Get current user's organization**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_org_admin=true` + membership |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Acme Tech",
    "slug": "acme-tech",
    "description": "Leading tech company in Nigeria",
    "logo_url": "",
    "website_url": "https://acmetech.com",
    "industry": { "id": 1, "name": "Technology" },
    "company_size": "51-200",
    "city": "Lagos",
    "state": "Lagos State",
    "country": "Nigeria",
    "is_verified": true
  },
  "meta": { "user_role": "owner" }
}
```

---

### PATCH `/organizations/me/`
**Update organization details**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_org_admin=true` + `owner`/`admin` role |

**Request Body:**
```json
{
  "description": "Updated description...",
  "website_url": "https://newsite.com",
  "company_size": "201-500",
  "city": "Abuja"
}
```

---

### GET `/organizations/me/talent-search/`
**Search talent profiles (Proactive Sourcing)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_org_admin=true` |

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search in headline, bio, name |
| `skills` | string | Comma-separated skill IDs (e.g., `1,2,3`) |
| `education_route` | string | Filter by education |
| `is_school_verified` | boolean | Filter verified only |
| `is_available` | boolean | Filter available only |
| `city` | string | Filter by city |
| `ordering` | string | `-created_at`, `headline` |

**Example:** `GET /organizations/me/talent-search/?skills=1,4&is_available=true&search=python`

---

## 6. Mentors

### GET `/mentors/me/`
**Get current user's mentor profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_mentor=true` |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user": { "id": 2, "email": "mentor@example.com", "full_name": "..." },
    "headline": "Senior Software Architect",
    "bio": "15+ years experience...",
    "expertise_areas": [
      { "id": 1, "name": "Python" },
      { "id": 4, "name": "Django" }
    ],
    "linkedin_url": "",
    "website_url": "",
    "is_accepting_mentees": true,
    "max_mentees": 5,
    "is_verified": false,
    "endorsements_given": 12
  }
}
```

---

### PATCH `/mentors/me/`
**Update mentor profile**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_mentor=true` |

**Request Body:**
```json
{
  "headline": "Senior Architect & Tech Mentor",
  "bio": "Updated bio...",
  "expertise_area_ids": [1, 4, 5],
  "linkedin_url": "https://linkedin.com/in/mentor",
  "is_accepting_mentees": true,
  "max_mentees": 10
}
```

---

### POST `/mentors/me/endorsements/`
**Endorse a talent's skill**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_mentor=true` |

**Request Body:**
```json
{
  "talent_profile_id": 1,
  "skill_id": 1,
  "endorsement_note": "Demonstrated excellent Python skills in our guided project."
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "talent_profile_id": 1,
    "talent_name": "John Doe",
    "skill": { "id": 1, "name": "Python" },
    "is_endorsed": true,
    "endorsed_at": "2024-01-20T15:30:00Z",
    "endorsement_note": "..."
  }
}
```

---

### GET `/mentors/me/endorsements/`
**List all endorsements given by mentor**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_mentor=true` |

---

## 7. Opportunities

### GET `/opportunities/`
**List all open opportunities (Public)**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search title, description |
| `opportunity_type` | string | `internship`, `micro_project`, `guided_project` |
| `is_remote` | boolean | Remote opportunities |
| `is_paid` | boolean | Paid opportunities |
| `skills` | string | Required skill IDs (comma-separated) |
| `organization` | integer | Filter by org ID |
| `ordering` | string | `-created_at`, `title`, `application_deadline` |

**Example:** `GET /opportunities/?is_remote=true&is_paid=true&skills=1,4`

---

### POST `/opportunities/`
**Create a new opportunity**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_org_admin=true` OR `is_mentor=true` |

**Request Body:**
```json
{
  "title": "Backend Developer Internship",
  "description": "Join our team to build scalable APIs...",
  "opportunity_type": "internship",
  "location": "Lagos, Nigeria",
  "is_remote": false,
  "experience_level": "entry",
  "duration": "3 months",
  "is_paid": true,
  "compensation": "₦150,000/month",
  "application_deadline": "2024-03-01T23:59:59Z",
  "start_date": "2024-03-15",
  "spots_available": 3,
  "max_applicants": 100,
  "required_skill_ids": [1, 4, 5]
}
```

| Field | Type | Required | Options |
|-------|------|----------|---------|
| `title` | string | ✅ | Max 200 chars |
| `description` | string | ✅ | Full details |
| `opportunity_type` | string | ✅ | `internship`, `micro_project`, `guided_project` |
| `location` | string | ❌ | City/Region |
| `is_remote` | boolean | ❌ | Default: false |
| `experience_level` | string | ❌ | `entry`, `intermediate`, `senior` |
| `duration` | string | ❌ | e.g., "3 months" |
| `is_paid` | boolean | ❌ | Default: false |
| `compensation` | string | ❌ | e.g., "₦150,000/month" |
| `application_deadline` | datetime | ❌ | ISO 8601 |
| `start_date` | date | ❌ | ISO 8601 |
| `spots_available` | integer | ❌ | Number of positions |
| `max_applicants` | integer | ❌ | Cap on applications |
| `required_skill_ids` | array | ❌ | Skill IDs |

---

### GET `/opportunities/<id>/`
**Get opportunity details (Public)**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

---

### PATCH `/opportunities/<id>/`
**Update opportunity (Owner only)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Must own the opportunity |

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description...",
  "status": "closed",
  "spots_available": 5
}
```

| `status` Options |
|------------------|
| `draft`, `published`, `closed`, `filled` |

---

### GET `/opportunities/<id>/applications/`
**List applications for an opportunity (Owner only)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Must own the opportunity |

**Query Parameters:**
| Param | Type | Options |
|-------|------|---------|
| `status` | string | `pending`, `reviewing`, `shortlisted`, `accepted`, `rejected`, `withdrawn` |

---

## 8. Applications

### POST `/opportunities/<opportunity_id>/apply/`
**Apply to an opportunity**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` + TalentProfile |

**Request Body:**
```json
{
  "cover_letter": "I am excited to apply for this position because...",
  "resume_url": "https://storage.supabase.com/resumes/my-resume.pdf",
  "additional_notes": "I am available to start immediately."
}
```

| Field | Type | Required |
|-------|------|----------|
| `cover_letter` | string | ❌ |
| `resume_url` | string | ❌ |
| `additional_notes` | string | ❌ |

**Errors:**
| Code | Message |
|------|---------|
| 403 | "Only talents can apply to opportunities." |
| 400 | "Please complete your talent profile before applying." |
| 400 | "This opportunity is not accepting applications." |
| 409 | "You have already applied to this opportunity." |

---

### GET `/opportunities/my-applications/`
**List current user's applications**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "opportunity": { "id": 1, "title": "Backend Developer Internship", "organization": "Acme Tech" },
      "status": "pending",
      "cover_letter": "...",
      "created_at": "2024-01-15T10:00:00Z",
      "reviewed_at": null,
      "reviewer_notes": null
    }
  ],
  "meta": { "count": 1 }
}
```

---

### PATCH `/opportunities/applications/<id>/status/`
**Update application status (Opportunity owner only)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | Must own the opportunity |

**Request Body:**
```json
{
  "status": "shortlisted",
  "reviewer_notes": "Strong Python skills. Schedule interview."
}
```

| `status` Options |
|------------------|
| `pending`, `reviewing`, `shortlisted`, `accepted`, `rejected`, `withdrawn` |

---

## 9. Schools & Verification

### GET `/schools/me/`
**Get school profile (School Admin)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_school_admin=true` + assigned to school |

---

### GET `/schools/me/roster/`
**List student roster records**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_school_admin=true` |

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `has_consented` | boolean | Filter by consent status |
| `search` | string | Search matric number, name, email |

---

### POST `/schools/me/roster/`
**Add student roster record**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_school_admin=true` |

**Request Body:**
```json
{
  "matriculation_number": "MAT2024001",
  "email": "student@unilag.edu.ng",
  "full_name": "Chioma Okafor",
  "department": "Computer Science",
  "course_of_study": "BSc Computer Science",
  "enrollment_year": 2020,
  "expected_graduation_year": 2024,
  "graduation_year": null,
  "is_graduated": false,
  "cgpa": 3.85
}
```

---

### POST `/schools/consent/`
**Consent to school data sharing (Talent)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` + TalentProfile |

**Request Body:**
```json
{
  "matriculation_number": "MAT2020001",
  "school_id": 1
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "verified": true,
    "school_name": "University of Lagos",
    "matriculation_number": "MAT2020001",
    "course_of_study": "BSc Computer Science",
    "department": "Computer Science",
    "is_graduated": false
  },
  "meta": { "message": "Your academic records have been verified successfully!" }
}
```

---

### GET `/schools/verification-status/`
**Check verification status (Talent)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes | `is_talent=true` |

---

## 11. Mentorship CRUD

The mentorship subsystem has TWO surfaces — mentor-side and talent-side —
sharing the same `MentorshipRelationship`, `MentorSession`, and
`MenteeActivity` tables. Authorization is enforced per relationship: a
mentor only sees relationships where `mentor=their MentorProfile`; a talent
only sees ones where `talent=their TalentProfile`.

`MentorSession.private_notes` is mentor-only and NEVER appears in talent-side
responses.

### Mentor-side

#### GET `/mentors/me/mentorships/`
List the mentor's mentorships. Optional `?status=active|paused|ended`.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 5,
      "mentor": {"id": 3, "email": "mentor@x.com", "full_name": "...", "headline": "...", "is_verified": true},
      "talent": {"id": 17, "email": "...", "full_name": "...", "headline": "..."},
      "status": "active",
      "focus_area": "System design for backend roles",
      "started_at": "2026-04-10T09:30:00Z",
      "ended_at": null
    }
  ]
}
```

#### POST `/mentors/me/mentorships/`
Mentor creates a relationship.

**Body:** `{"talent_profile_id": 17, "focus_area": "System design"}`

**Errors:** `409 conflict` if a relationship with that talent already exists.

#### GET `/mentors/me/mentorships/<id>/`
Single relationship detail.

#### PATCH `/mentors/me/mentorships/<id>/`
**Body:** `{"status": "paused" | "ended" | "active", "focus_area": "..."}`

Transitioning to `ended` automatically stamps `ended_at`.

#### GET `/mentors/me/mentorships/<id>/sessions/`
List sessions in this relationship (includes `private_notes`).

#### POST `/mentors/me/mentorships/<id>/sessions/`
Create a session.

**Body:**
```json
{
  "scheduled_for": "2026-05-20T15:00:00Z",
  "duration_minutes": 45,
  "status": "scheduled",
  "topic": "Indexing strategies",
  "private_notes": ""
}
```

#### GET / PATCH / DELETE `/mentors/me/sessions/<id>/`
Individual session ops. Mentor must own it.

#### GET `/mentors/me/mentorships/<id>/activities/`
Read the mentee's logged activities.

---

### Talent-side

#### GET `/talents/me/mentorships/`
Talent's mentorships. Read-only.

#### GET `/talents/me/mentorships/<id>/`
Single relationship.

#### GET `/talents/me/mentorships/<id>/sessions/`
Sessions in this relationship — `private_notes` is **omitted**.

#### GET `/talents/me/mentorships/<id>/activities/`
List own activities in this relationship.

#### POST `/talents/me/mentorships/<id>/activities/`
Talent self-logs an activity.

**Body:**
```json
{
  "activity_type": "project_shipped",
  "description": "Shipped v1 of recipe-app",
  "metadata": {"repo_url": "https://github.com/me/recipe-app"},
  "occurred_at": "2026-05-18T14:00:00Z"
}
```

`activity_type` ∈ `skill_added`, `skill_endorsed`, `application_submitted`, `application_accepted`, `project_shipped`, `blocker_reported`, `note`.

#### PATCH / DELETE `/talents/me/activities/<id>/`
Talent edits/removes their own log.

---

## 12. AI Engine

All AI endpoints share these error codes:

| HTTP | code              | Meaning                                     |
|------|-------------------|---------------------------------------------|
| 401  | not_authenticated | Missing/invalid JWT                         |
| 503  | ai_disabled       | `GEMINI_API_KEY` is not configured          |
| 502  | ai_unavailable    | Gemini / Supabase returned an error         |
| 504  | ai_timeout        | AI call exceeded `AI_CALL_TIMEOUT_SECONDS`  |

Cached endpoints (Trust Score, Skill Roadmap, Curriculum Alignment) accept
`?refresh=true` to force recomputation. Default TTL is 24h.

---

### POST `/ai/match-cv/`
**Run a CV against uncompared company requirements (Supabase script wrapper)**

| Auth Required | Role Required |
|---------------|---------------|
| ✅ Yes        | Any           |

**Request Body:**
```json
{
  "name": "Jane Smith",
  "skills": ["React", "TypeScript", "Node.js"],
  "experience": "Senior Frontend Engineer, 5 years"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "matched_requirement_ids": ["uuid-1", "uuid-2"],
    "matched_count": 2
  }
}
```

---

### GET `/ai/trust-score/me/`
**Calling talent's own Trust Score (deterministic 0-100 + LLM rationale)**

| Auth Required | Role Required          |
|---------------|------------------------|
| ✅ Yes        | Must have TalentProfile|

**Query Params:** `?refresh=true` to force recompute.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "payload": {
      "score": 72,
      "components": {
        "endorsements": 32,
        "school_verification": 25,
        "academic_performance": 0,
        "profile_completeness": 16
      },
      "signals": {
        "endorsements": {"endorsed": 4, "total": 6, "ratio": 0.67},
        "school_verification": {"verified": true},
        "academic_performance": {"cgpa": null, "note": "not_provided"},
        "profile_completeness": {"bio": true, "headline": true, "github_or_portfolio": true, "linkedin": false, "has_skills": true}
      },
      "weights": {"endorsements": 40, "school_verification": 25, "academic_performance": 15, "profile_completeness": 20},
      "rationale": "Strong verified credentials and mentor-endorsed skills. Adding LinkedIn would round out the profile."
    },
    "was_recomputed": false
  }
}
```

---

### GET `/ai/trust-score/talents/<id>/`
**Trust Score for any talent (e.g. employer viewing a profile)**

Same response shape as `/me/`. Any authenticated user may call.

---

### GET `/ai/skill-roadmap/me/`
**Personalized learning roadmap based on market demand**

| Auth Required | Role Required          |
|---------------|------------------------|
| ✅ Yes        | Must have TalentProfile|

Aggregates the most-required skills across open opportunities (biased toward
the talent's `field_of_study`), filters out skills the talent already has,
and asks the LLM for a 3-5 step actionable plan.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "payload": {
      "current_skills": [{"skill__name": "Python", "proficiency": "advanced"}],
      "top_gaps": [
        {"skill_id": 9, "skill_name": "Docker", "demand_count": 14},
        {"skill_id": 10, "skill_name": "Machine Learning", "demand_count": 11}
      ],
      "field_of_study": "Computer Science",
      "summary": "Your biggest gap is containerization, which appears in most backend roles.",
      "steps": [
        {"order": 1, "title": "Containerize a side project with Docker", "skill": "Docker", "rationale": "...", "suggested_action": "Look for guided projects tagged `docker` on the platform."}
      ]
    },
    "was_recomputed": true
  }
}
```

---

### GET `/ai/opportunities/<id>/talent-matches/`
**LLM-ranked talents for an opportunity (Predictive sourcing)**

| Auth Required | Role Required                                |
|---------------|----------------------------------------------|
| ✅ Yes        | Opportunity creator OR member of posting org |

Pre-filters TalentProfiles that share ≥1 required skill and are `is_available`,
caps at 20, sends to Gemini for ranking. Not cached.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "opportunity_id": 42,
    "matches": [
      {
        "talent_id": 17,
        "rank": 1,
        "fit_score": 88,
        "reason": "Endorsed in Python and Django; verified by UNILAG.",
        "talent": {"id": 17, "full_name": "Chioma O.", "headline": "...", "is_school_verified": true}
      }
    ]
  }
}
```

---

### GET `/ai/mentor-matches/`
**Top mentor matches for the calling talent**

| Auth Required | Role Required          |
|---------------|------------------------|
| ✅ Yes        | Must have TalentProfile|

Prioritizes mentors whose `expertise_areas` cover the talent's skill **gaps**
(not skills they already have). Not cached.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "matches": [
      {
        "mentor_id": 3,
        "rank": 1,
        "fit_score": 92,
        "reason": "Specializes in Kubernetes and Cloud — your top market gap.",
        "mentor": {"id": 3, "full_name": "...", "headline": "...", "is_verified": true, "expertise": ["Kubernetes", "AWS"]}
      }
    ]
  }
}
```

---

### GET `/ai/organizations/<id>/proactive-sourcing/`
**Predictive talent sourcing — surfaces "hidden gems" who haven't applied yet**

| Auth Required | Role Required                       |
|---------------|-------------------------------------|
| ✅ Yes        | Member of the target organization   |

Builds a "successful applicant" pattern from past accepted/shortlisted
applications, then ranks similar talents who have NOT yet applied. Not cached.

**Confidence levels:**
- `low` — fewer than 5 past hires; pattern is weak.
- `medium` — 5+ past hires; pattern is meaningful but still narrow.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "organization_id": 1,
    "confidence": "low",
    "confidence_reason": "Based on 2 past hire(s). Confidence will improve as you fill more opportunities.",
    "past_hire_count": 2,
    "matches": [
      {
        "talent_id": 47,
        "rank": 1,
        "fit_score": 74,
        "reason": "Matches your Python+Django pattern; school-verified. Low confidence due to small history.",
        "talent": {"id": 47, "full_name": "...", "headline": "...", "is_school_verified": true}
      }
    ]
  }
}
```

---

### GET `/ai/mentorships/<id>/progress-insight/`
**Pre-session brief for a mentor about their mentee's recent activity**

| Auth Required | Role Required                                |
|---------------|----------------------------------------------|
| ✅ Yes        | Must be the mentor in this MentorshipRelationship |

Reads the last 10 `MenteeActivity` events and last 3 completed
`MentorSession` rows, asks Gemini for a wins/blockers/topics brief.
Returns a graceful "no activity logged" payload when the relationship is new.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "mentorship_id": 5,
    "payload": {
      "mentee_name": "Chioma O.",
      "focus_area": "System design for backend roles",
      "summary": "Chioma shipped 2 side projects this week but is stuck on database indexing.",
      "wins": ["Shipped recipe-app v1 with Postgres", "Got Python endorsement from peer mentor"],
      "blockers": ["Indexing strategy for multi-tenant schema"],
      "suggested_topics": ["Compound indexes vs single-column", "When to denormalize"],
      "note_if_no_activity": null,
      "recent_activities": [...],
      "recent_sessions": [...]
    }
  }
}
```

---

### GET `/ai/schools/<id>/curriculum-alignment/`
**Curriculum-to-market alignment report (School admin)**

| Auth Required | Role Required               |
|---------------|-----------------------------|
| ✅ Yes        | Admin of the target school  |

Aggregates the school's consented roster (departments, graduates), compares
their claimed skills to platform-wide market demand, asks the LLM to flag
under-represented skills and well-aligned departments.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "payload": {
      "school_name": "University of Lagos",
      "departments": [{"department": "Computer Science", "course_of_study": "BSc CS", "count": 42}],
      "graduate_count": 137,
      "talent_skill_counts": {"Python": 88, "Docker": 11},
      "market_demand": [{"skill_id": 9, "skill_name": "Docker", "demand_count": 34}],
      "summary": "Your CS programme over-indexes on Python but under-prepares for DevOps tooling.",
      "underrepresented_skills": [
        {"skill": "Docker", "market_demand": 34, "current_graduates_with_skill": 11, "recommendation": "Add a 200-level containerization elective."}
      ],
      "well_aligned_departments": ["Computer Science: Web Development track"]
    },
    "was_recomputed": false
  }
}
```

---

## 13. Taxonomy

### Skills & Industries
These are seeded via `python manage.py seed_data`. To retrieve:

**Skills:** Available via `/api/schema/` or Django Admin  
**Industries:** Available via `/api/schema/` or Django Admin

| Skill ID | Name |
|----------|------|
| 1 | Python |
| 2 | JavaScript |
| 3 | React |
| 4 | Django |
| 5 | PostgreSQL |
| 6 | Node.js |
| 7 | TypeScript |
| 8 | AWS |
| 9 | Docker |
| 10 | Machine Learning |

| Industry ID | Name |
|-------------|------|
| 1 | Technology |
| 2 | Finance |
| 3 | Healthcare |
| 4 | Education |
| 5 | E-commerce |
| 6 | Logistics |
| 7 | Agriculture |
| 8 | Energy |

---

## 🔐 Test Accounts

| Email | Password | Roles |
|-------|----------|-------|
| `talent@skillbridge.com` | `TestPassword123!` | Talent |
| `orgadmin@skillbridge.com` | `TestPassword123!` | Org Admin (Acme Tech) |
| `mentor@skillbridge.com` | `TestPassword123!` | Mentor |
| `schooladmin@skillbridge.com` | `TestPassword123!` | School Admin (UNILAG) |
| `multi@skillbridge.com` | `TestPassword123!` | Talent + Mentor |

---

## 📊 Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Duplicate resource |
| 500 | Server Error |

**Error Response Format:**
```json
{
  "status": "error",
  "data": null,
  "meta": { "http_status": 403 },
  "errors": [
    {
      "field": null,
      "message": "You don't have permission to perform this action.",
      "code": "not_owner"
    }
  ]
}
```

---

## 🚀 Quick Start

1. **Get a token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signin/" \
  -H "Content-Type: application/json" \
  -d '{"email": "talent@skillbridge.com", "password": "TestPassword123!"}'
```

2. **Use the token:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

3. **Create an application:**
```bash
curl -X POST "http://localhost:8000/api/v1/opportunities/1/apply/" \
  -H "Authorization: Bearer TALENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cover_letter": "I am very interested in this position..."}'
```