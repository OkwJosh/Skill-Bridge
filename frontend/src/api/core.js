import { apiRequest } from './client';

// GET /core/skills/?category=&search=
export const getSkills = (params = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v);
  });
  const s = qs.toString();
  return apiRequest(`/core/skills/${s ? `?${s}` : ''}`);
};

// POST /core/skills/   — find-or-create by name. Returns 200 if found, 201 if created.
export const createSkill = (name) =>
  apiRequest('/core/skills/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });

// GET /core/industries/
export const getIndustries = () => apiRequest('/core/industries/');
