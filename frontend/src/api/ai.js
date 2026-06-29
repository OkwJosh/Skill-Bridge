import { apiRequest } from './client';

// ─── Legacy: CV match against Supabase requirements ─────────────────────────
// POST /ai/match-cv/
// Returns { matched_requirement_ids: string[], matched_count: number }
export const matchCv = ({ name, skills, experience }, { signal } = {}) =>
  apiRequest('/ai/match-cv/', {
    method: 'POST',
    body: JSON.stringify({ name, skills, experience }),
    signal,
  });


// ─── Trust Score ────────────────────────────────────────────────────────────
// All cached endpoints accept ?refresh=true to force recompute.
//
// Response shape (inner data, envelope already unwrapped by client.js):
//   { payload: { score, components, signals, weights, rationale }, was_recomputed }

export const getMyTrustScore = ({ refresh = false } = {}) =>
  apiRequest(`/ai/trust-score/me/${refresh ? '?refresh=true' : ''}`);

export const getTalentTrustScore = (talentId, { refresh = false } = {}) =>
  apiRequest(`/ai/trust-score/talents/${talentId}/${refresh ? '?refresh=true' : ''}`);


// ─── Skill Roadmap ──────────────────────────────────────────────────────────
// Response: { payload: { summary, steps: [...], top_gaps, current_skills, ... }, was_recomputed }

export const getMySkillRoadmap = ({ refresh = false } = {}) =>
  apiRequest(`/ai/skill-roadmap/me/${refresh ? '?refresh=true' : ''}`);


// ─── Project ↔ Talent Match (org owner of opportunity) ──────────────────────
// Response: { opportunity_id, matches: [{ talent_id, rank, fit_score, reason, talent: {...} }] }

export const getOpportunityTalentMatches = (opportunityId) =>
  apiRequest(`/ai/opportunities/${opportunityId}/talent-matches/`);


// ─── Mentor ↔ Mentee Match (talent finds mentors) ───────────────────────────
// Response: { matches: [{ mentor_id, rank, fit_score, reason, mentor: {...} }] }

export const getMentorMatches = () => apiRequest('/ai/mentor-matches/');


// ─── Curriculum Alignment (school admin) ────────────────────────────────────
// Response: { payload: { summary, underrepresented_skills, well_aligned_departments, ... }, was_recomputed }

export const getCurriculumAlignment = (schoolId, { refresh = false } = {}) =>
  apiRequest(`/ai/schools/${schoolId}/curriculum-alignment/${refresh ? '?refresh=true' : ''}`);


// ─── Predictive Talent Sourcing (org admin/member) ──────────────────────────
// Response: { organization_id, confidence: 'low'|'medium', confidence_reason, past_hire_count, matches: [...] }

export const getProactiveSourcing = (organizationId) =>
  apiRequest(`/ai/organizations/${organizationId}/proactive-sourcing/`);


// ─── Mentee Progress Insight (mentor pre-session brief) ─────────────────────
// Response: { mentorship_id, payload: { mentee_name, focus_area, summary, wins, blockers, suggested_topics, ... } }

export const getMenteeProgressInsight = (mentorshipId) =>
  apiRequest(`/ai/mentorships/${mentorshipId}/progress-insight/`);
