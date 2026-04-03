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

**Request Body:**
```json
{
  "email": "user@example.com",
  "redirect_url": "https://yourapp.com/reset-password"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": { "message": "If an account with this email exists, a password reset link has been sent." }
}
```

---

### POST `/auth/password/confirm/`
**Set new password after reset**

| Auth Required | Role Required |
|---------------|---------------|
| ❌ No | None |

**Request Body:**
```json
{
  "access_token": "token_from_reset_link",
  "new_password": "NewSecurePass123!"
}
```

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

## 10. Taxonomy

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