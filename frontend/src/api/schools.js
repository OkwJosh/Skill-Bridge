import { apiRequest, uploadFile } from './client';

// POST /schools/   — first-time setup for a school admin
export const createMySchool = (data) =>
  apiRequest('/schools/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

// GET /schools/me/   — school admin's school
export const getMySchool = () => apiRequest('/schools/me/');

// POST /schools/me/roster/import/?mode=skip|upsert  (multipart/form-data)
export const importRosterCSV = (file, mode = 'skip') =>
  uploadFile(`/schools/me/roster/import/?mode=${mode}`, file);

// GET /schools/me/roster/?has_consented=&search=
export const listRoster = (params = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v);
  });
  const s = qs.toString();
  return apiRequest(`/schools/me/roster/${s ? `?${s}` : ''}`);
};

// POST /schools/me/roster/
export const addRosterRecord = (data) =>
  apiRequest('/schools/me/roster/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

// POST /schools/consent/   (talent-side, kept here for completeness)
export const consentToSchool = ({ matriculation_number, school_id }) =>
  apiRequest('/schools/consent/', {
    method: 'POST',
    body: JSON.stringify({ matriculation_number, school_id }),
  });

// GET /schools/verification-status/  (talent-side)
export const getVerificationStatus = () => apiRequest('/schools/verification-status/');
