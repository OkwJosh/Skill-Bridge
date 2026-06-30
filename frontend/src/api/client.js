// ─── Base API Client ─────────────────────────────────────────────
// All requests go through here. Handles auth headers, token refresh,
// and the standard { status, data, errors } envelope from the backend.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://skill-bridge-8thk.onrender.com/api/v1';

// Pull token from localStorage (set by AuthContext on login)
const getToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');

// Save tokens after login / refresh
export const saveTokens = ({ access_token, refresh_token }) => {
  localStorage.setItem('access_token', access_token);
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
};

// Clear tokens on logout
export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Try to refresh the access token silently
let isRefreshing = false;
async function refreshAccessToken() {
  if (isRefreshing) return null;
  isRefreshing = true;
  try {
    const refresh_token = getRefreshToken();
    if (!refresh_token) return null;

    const res = await fetch(`${BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token }),
    });
    const json = await res.json();
    if (json.status === 'success') {
      saveTokens(json.data);
      return json.data.access_token;
    }
    return null;
  } catch {
    return null;
  } finally {
    isRefreshing = false;
  }
}

// ─── Core request function ────────────────────────────────────────
export async function apiRequest(path, options = {}, retry = true) {
  const token = getToken();

  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });

  // Token expired — only attempt refresh if we *had* a token going in.
  // A 401 with no prior token is a credential failure (e.g. wrong password
  // on /auth/signin/), NOT an expired session; bubbling it up via the
  // normal error path lets the caller display the real error message.
  if (res.status === 401 && retry && token) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return apiRequest(path, options, false); // retry with new token
    }
    // Refresh failed — wipe creds and re-throw so the caller sees the error.
    clearTokens();
    throw new Error('Your session has expired. Please sign in again.');
  }

  const json = await res.json().catch(() => ({}));

  // Backend uses { status: 'error', errors: [...] } envelope
  if (!res.ok || json.status === 'error') {
    const message =
      json.errors?.[0]?.message ||
      json.detail ||
      `Request failed (${res.status})`;
    throw new Error(message);
  }

  // Return the inner data object directly
  return json.data ?? json;
}

// ─── Multipart upload helper ───────────────────────────────────────
// Posts a single File to the backend without setting Content-Type
// (browser sets the multipart boundary). Used by CSV roster import,
// and any other backend endpoint that accepts multipart form data.
export async function uploadFile(path, file, { fieldName = 'file' } = {}) {
  const token = getToken();
  const form = new FormData();
  form.append(fieldName, file);

  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || json.status === 'error') {
    const message =
      json.errors?.[0]?.message ||
      json.detail ||
      `Upload failed (${res.status})`;
    throw new Error(message);
  }
  return json.data ?? json;
}
