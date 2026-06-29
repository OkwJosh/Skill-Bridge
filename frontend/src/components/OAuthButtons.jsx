/**
 * OAuthButtons — Google + Apple sign-in for SkillBridge.
 *
 * Loads each provider's JS SDK on demand (no script tags in index.html).
 * Hides each button when its corresponding env var is missing
 * (VITE_GOOGLE_CLIENT_ID, VITE_APPLE_SERVICE_ID) so the rest of the page
 * still works without OAuth credentials provisioned.
 *
 * On success, posts the provider's ID token to the backend via
 * AuthContext.loginWithOAuth(...) and navigates to either:
 *   - /choose-role           if user.needs_onboarding
 *   - /app/home              otherwise
 */

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
const APPLE_SERVICE_ID = import.meta.env.VITE_APPLE_SERVICE_ID || '';
const APPLE_REDIRECT_URI = import.meta.env.VITE_APPLE_REDIRECT_URI || (typeof window !== 'undefined' ? window.location.origin : '');

const GOOGLE_SDK_URL = 'https://accounts.google.com/gsi/client';
const APPLE_SDK_URL = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js';


// ── Generic script loader (idempotent, caches by src) ─────────────────────
const _loaded = new Map(); // src -> Promise
function loadScript(src) {
  if (_loaded.has(src)) return _loaded.get(src);
  const p = new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
    const s = document.createElement('script');
    s.src = src;
    s.async = true;
    s.defer = true;
    s.onload = resolve;
    s.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(s);
  });
  _loaded.set(src, p);
  return p;
}


export default function OAuthButtons({ onError }) {
  const navigate = useNavigate();
  const { loginWithOAuth } = useAuth();
  const [busy, setBusy] = useState(null); // 'google' | 'apple' | null
  const googleBtnRef = useRef(null);

  const googleEnabled = !!GOOGLE_CLIENT_ID;
  const appleEnabled  = !!APPLE_SERVICE_ID;

  // ── Common post-auth routing ────────────────────────────────────────────
  const finish = async (provider, idToken) => {
    setBusy(provider);
    try {
      const user = await loginWithOAuth(provider, idToken);
      navigate(user.needs_onboarding ? '/choose-role' : '/app/home', { replace: true });
    } catch (err) {
      onError?.(err.message || `${provider} sign-in failed`);
    } finally {
      setBusy(null);
    }
  };

  // ── Google: render official GIS button ──────────────────────────────────
  useEffect(() => {
    if (!googleEnabled || !googleBtnRef.current) return;
    let cancelled = false;
    loadScript(GOOGLE_SDK_URL).then(() => {
      if (cancelled || !window.google?.accounts?.id) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (resp) => finish('google', resp.credential),
        ux_mode: 'popup',
        auto_select: false,
      });
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: 'icon',
        shape: 'circle',
        size: 'large',
      });
    }).catch((e) => onError?.(e.message));
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [googleEnabled]);

  // ── Apple: load SDK lazily, trigger popup on click ──────────────────────
  const handleAppleClick = async () => {
    if (!appleEnabled) return;
    try {
      await loadScript(APPLE_SDK_URL);
      window.AppleID.auth.init({
        clientId: APPLE_SERVICE_ID,
        scope: 'name email',
        redirectURI: APPLE_REDIRECT_URI,
        usePopup: true,
      });
      const result = await window.AppleID.auth.signIn();
      // result.authorization.id_token is the JWT we POST to the backend
      const idToken = result?.authorization?.id_token;
      if (!idToken) throw new Error('Apple did not return an ID token.');
      await finish('apple', idToken);
    } catch (err) {
      // User-cancelled popups come back with err.error === 'popup_closed_by_user'
      if (err?.error !== 'popup_closed_by_user') {
        onError?.(err.message || 'Apple sign-in failed');
      }
    }
  };

  // If neither provider is configured, render nothing.
  if (!googleEnabled && !appleEnabled) return null;

  return (
    <div className="flex justify-center gap-4 mb-6">
      {googleEnabled && (
        <div
          ref={googleBtnRef}
          aria-label="Sign in with Google"
          style={{ opacity: busy === 'google' ? 0.5 : 1 }}
        />
      )}
      {appleEnabled && (
        <button
          onClick={handleAppleClick}
          disabled={busy === 'apple'}
          aria-label="Sign in with Apple"
          className="w-12 h-12 rounded-full border flex items-center justify-center hover:bg-gray-50 text-lg disabled:opacity-50"
          style={{ borderColor: 'var(--border)' }}
        >
          🍎
        </button>
      )}
    </div>
  );
}
