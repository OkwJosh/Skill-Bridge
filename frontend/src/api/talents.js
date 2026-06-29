import { apiRequest } from './client';

// GET /talents/   — list talents (any auth'd user)
// Params: search, skills (csv ids), is_available, ordering, limit
export const listTalents = (params = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v);
  });
  const s = qs.toString();
  return apiRequest(`/talents/${s ? `?${s}` : ''}`);
};

// GET /talents/me/
export const getMyTalentProfile = () => apiRequest('/talents/me/');

// GET /talents/me/mentorships/   — the talent's own mentorships (their mentors)
export const listMyMentorshipsAsTalent = (status) =>
  apiRequest(`/talents/me/mentorships/${status ? `?status=${status}` : ''}`);

// GET /talents/<id>/ — read any talent's public profile
export const getTalentProfile = (id) => apiRequest(`/talents/${id}/`);

// PATCH /talents/me/
export const updateMyTalentProfile = (data) =>
  apiRequest('/talents/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// POST /talents/me/skills/
export const addSkill = ({ skill_id, proficiency, years_experience, is_primary }) =>
  apiRequest('/talents/me/skills/', {
    method: 'POST',
    body: JSON.stringify({ skill_id, proficiency, years_experience, is_primary }),
  });

// PATCH /talents/me/skills/<skill_id>/
export const updateSkill = (skillId, data) =>
  apiRequest(`/talents/me/skills/${skillId}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// DELETE /talents/me/skills/<skill_id>/
export const removeSkill = (skillId) =>
  apiRequest(`/talents/me/skills/${skillId}/`, { method: 'DELETE' });
