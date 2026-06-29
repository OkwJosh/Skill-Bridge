import { apiRequest } from './client';

// POST /auth/signup/
export const signup = ({ email, password, full_name, phone_number, role = 'talent' }) =>
  apiRequest('/auth/signup/', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, phone_number, role }),
  });

// POST /auth/signin/
export const signin = ({ email, password }) =>
  apiRequest('/auth/signin/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

// POST /auth/signout/
export const signout = () =>
  apiRequest('/auth/signout/', { method: 'POST' });

// GET /auth/me/
export const getMe = () => apiRequest('/auth/me/');

// PATCH /auth/me/
export const updateMe = (data) =>
  apiRequest('/auth/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });

// POST /auth/password/reset/
// Backend silently returns 200 even if the email isn't registered (anti-enumeration).
export const requestPasswordReset = (email) =>
  apiRequest('/auth/password/reset/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });

// POST /auth/password/confirm/
export const confirmPasswordReset = ({ uid, token, new_password }) =>
  apiRequest('/auth/password/confirm/', {
    method: 'POST',
    body: JSON.stringify({ uid, token, new_password }),
  });

// POST /auth/email/verify/   Body: {uid, token}
export const verifyEmail = ({ uid, token }) =>
  apiRequest('/auth/email/verify/', {
    method: 'POST',
    body: JSON.stringify({ uid, token }),
  });

// POST /auth/email/resend/   (auth required)
export const resendVerificationEmail = () =>
  apiRequest('/auth/email/resend/', { method: 'POST' });

// POST /auth/google/   Body: {id_token}
export const signInWithGoogle = (idToken) =>
  apiRequest('/auth/google/', {
    method: 'POST',
    body: JSON.stringify({ id_token: idToken }),
  });

// POST /auth/apple/    Body: {id_token}
export const signInWithApple = (idToken) =>
  apiRequest('/auth/apple/', {
    method: 'POST',
    body: JSON.stringify({ id_token: idToken }),
  });
