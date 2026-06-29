/**
 * Pre-signed upload helpers
 * =========================
 *
 * Two-step upload:
 *   1) Ask backend for a signed PUT URL  →  POST /core/uploads/sign/
 *   2) PUT the file bytes directly to Supabase Storage at that URL
 *
 * The file bytes never traverse our API server, which keeps avatar /
 * resume uploads cheap and fast.
 *
 * Usage:
 *   const url = await uploadToSupabase(file, 'avatar');
 *   await updateMe({ avatar_url: url });
 */

import { apiRequest } from './client';

// POST /core/uploads/sign/
export const requestSignedUpload = ({ purpose, filename, contentType, size }) =>
  apiRequest('/core/uploads/sign/', {
    method: 'POST',
    body: JSON.stringify({
      purpose,
      filename,
      content_type: contentType,
      size,
    }),
  });

/**
 * Upload a File to Supabase Storage via a pre-signed PUT URL.
 *
 * Returns the persistent `public_url` you should store on the model
 * (e.g. User.avatar_url, Application.resume_url).
 */
export async function uploadToSupabase(file, purpose) {
  const signed = await requestSignedUpload({
    purpose,
    filename: file.name,
    contentType: file.type || 'application/octet-stream',
    size: file.size,
  });

  // Direct PUT — must match the Content-Type we declared at sign time,
  // otherwise the signature check fails.
  const putRes = await fetch(signed.upload_url, {
    method: 'PUT',
    headers: { 'Content-Type': file.type || 'application/octet-stream' },
    body: file,
  });
  if (!putRes.ok) {
    throw new Error(`Upload failed (${putRes.status} ${putRes.statusText})`);
  }
  return signed.public_url;
}
