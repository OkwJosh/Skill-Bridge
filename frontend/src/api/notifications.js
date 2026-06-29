import { apiRequest } from './client';

// GET /notifications/?is_read=true|false&limit=50
// Returns { items: [...], unread_count: number }
export const listNotifications = (params = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v);
  });
  const s = qs.toString();
  return apiRequest(`/notifications/${s ? `?${s}` : ''}`);
};

// POST /notifications/<id>/read/
export const markNotificationRead = (id) =>
  apiRequest(`/notifications/${id}/read/`, { method: 'POST' });

// POST /notifications/read-all/
export const markAllNotificationsRead = () =>
  apiRequest('/notifications/read-all/', { method: 'POST' });

// GET /notifications/unread-count/  — cheap badge poll
export const getUnreadNotificationCount = () =>
  apiRequest('/notifications/unread-count/');
