import { apiRequest } from './client';

// GET /opportunities/         — public, no auth needed
// Supports: search, opportunity_type, is_remote, is_paid, skills, ordering
export const getOpportunities = (params = {}) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') query.set(k, v);
  });
  const qs = query.toString();
  return apiRequest(`/opportunities/${qs ? `?${qs}` : ''}`);
};

// GET /opportunities/<id>/    — public
export const getOpportunity = (id) => apiRequest(`/opportunities/${id}/`);

// POST /opportunities/<id>/apply/   — requires talent auth
export const applyToOpportunity = (id, { cover_letter, resume_url, additional_notes }) =>
  apiRequest(`/opportunities/${id}/apply/`, {
    method: 'POST',
    body: JSON.stringify({ cover_letter, resume_url, additional_notes }),
  });

// GET /opportunities/my-applications/   — requires talent auth
export const getMyApplications = () => apiRequest('/opportunities/my-applications/');

// POST /opportunities/        — requires org_admin or mentor auth
export const createOpportunity = (data) =>
  apiRequest('/opportunities/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

// PATCH /opportunities/<id>/  — requires owner auth
export const updateOpportunity = (id, data) =>
  apiRequest(`/opportunities/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// GET /opportunities/<id>/applications/?status=...   — owner only
export const listOpportunityApplications = (opportunityId, status) =>
  apiRequest(`/opportunities/${opportunityId}/applications/${status ? `?status=${status}` : ''}`);

// PATCH /opportunities/applications/<id>/status/   — owner only
export const updateApplicationStatus = (applicationId, { status, reviewer_notes }) =>
  apiRequest(`/opportunities/applications/${applicationId}/status/`, {
    method: 'PATCH',
    body: JSON.stringify({ status, reviewer_notes }),
  });
