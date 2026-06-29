import { apiRequest } from './client';

// POST /organizations/   — first-time setup for an org admin.
export const createMyOrganization = (data) =>
  apiRequest('/organizations/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

// GET /organizations/me/
export const getMyOrganization = () => apiRequest('/organizations/me/');

// PATCH /organizations/me/
export const updateMyOrganization = (data) =>
  apiRequest('/organizations/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// GET /organizations/me/talent-search/?search=...&skills=1,2&is_available=true
export const searchTalent = (params = {}) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') query.set(k, v);
  });
  return apiRequest(`/organizations/me/talent-search/?${query.toString()}`);
};
