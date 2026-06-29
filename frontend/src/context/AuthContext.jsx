import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { signin, signup, signout, getMe, signInWithGoogle, signInWithApple } from '../api/auth';
import { saveTokens, clearTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // true while checking stored token

  // On app load — if a token exists in localStorage, fetch the current user
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => clearTokens()) // token was invalid/expired
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // ─── Login ──────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await signin({ email, password });
    // data = { user, access_token, refresh_token, expires_in }
    saveTokens(data);
    setUser(data.user);
    return data.user;
  }, []);

  // ─── Register ───────────────────────────────────────────────────
  const register = useCallback(async ({ email, password, full_name, phone_number, role = 'talent' }) => {
    const data = await signup({ email, password, full_name, phone_number, role });
    saveTokens(data);
    setUser(data.user);
    return data.user;
  }, []);

  // ─── OAuth sign-in (Google / Apple) ─────────────────────────────
  // Frontend gets idToken from the provider's JS SDK, sends it here,
  // backend verifies + issues our JWT pair. Returns the user so callers
  // can route based on `user.needs_onboarding`.
  const loginWithOAuth = useCallback(async (provider, idToken) => {
    const fn = provider === 'google' ? signInWithGoogle
             : provider === 'apple'  ? signInWithApple
             : null;
    if (!fn) throw new Error(`Unknown OAuth provider: ${provider}`);
    const data = await fn(idToken);
    saveTokens(data);
    setUser(data.user);
    return data.user;
  }, []);

  // ─── Logout ─────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    try { await signout(); } catch { /* ignore */ }
    clearTokens();
    setUser(null);
  }, []);

  // ─── Update user state after profile edit ───────────────────────
  const refreshUser = useCallback(async () => {
    const fresh = await getMe();
    setUser(fresh);
    return fresh;
  }, []);

  const value = {
    user,
    loading,
    isLoggedIn: !!user,
    isTalent: user?.is_talent ?? false,
    isOrgAdmin: user?.is_org_admin ?? false,
    isMentor: user?.is_mentor ?? false,
    needsOnboarding: user?.needs_onboarding ?? false,
    login,
    register,
    loginWithOAuth,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
