import { apiRequest } from './client';

// ─── Mentor profile ─────────────────────────────────────────────────────────
export const getMyMentorProfile = () => apiRequest('/mentors/me/');

export const updateMyMentorProfile = (data) =>
  apiRequest('/mentors/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// ─── Endorsements ───────────────────────────────────────────────────────────
// POST /mentors/me/endorsements/   { talent_profile_id, skill_id, endorsement_note }
export const createEndorsement = ({ talent_profile_id, skill_id, endorsement_note }) =>
  apiRequest('/mentors/me/endorsements/', {
    method: 'POST',
    body: JSON.stringify({ talent_profile_id, skill_id, endorsement_note }),
  });

export const listMyEndorsements = () => apiRequest('/mentors/me/endorsements/list/');

// ─── Mentorships (mentor-side CRUD) ─────────────────────────────────────────
export const listMyMentorships = (status) =>
  apiRequest(`/mentors/me/mentorships/${status ? `?status=${status}` : ''}`);

export const getMyMentorship = (id) =>
  apiRequest(`/mentors/me/mentorships/${id}/`);

export const createMentorship = ({ talent_profile_id, focus_area }) =>
  apiRequest('/mentors/me/mentorships/', {
    method: 'POST',
    body: JSON.stringify({ talent_profile_id, focus_area }),
  });

export const updateMentorship = (id, data) =>
  apiRequest(`/mentors/me/mentorships/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// ─── Sessions (mentor-side CRUD) ────────────────────────────────────────────
export const listSessions = (mentorshipId) =>
  apiRequest(`/mentors/me/mentorships/${mentorshipId}/sessions/`);

export const createSession = (mentorshipId, data) =>
  apiRequest(`/mentors/me/mentorships/${mentorshipId}/sessions/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const updateSession = (sessionId, data) =>
  apiRequest(`/mentors/me/sessions/${sessionId}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

export const deleteSession = (sessionId) =>
  apiRequest(`/mentors/me/sessions/${sessionId}/`, { method: 'DELETE' });

// ─── Mentee activities (mentor-read) ────────────────────────────────────────
export const listMentorActivities = (mentorshipId) =>
  apiRequest(`/mentors/me/mentorships/${mentorshipId}/activities/`);
