/**
 * VerifyEmailPage — landing page for the verification link in the email.
 *
 * URL: /verify-email?uid=<uidb64>&token=<token>
 *
 * On mount we POST the uid+token to /auth/email/verify/, refresh the
 * cached user so `email_verified` flips in AuthContext, then route them
 * to the app (or the sign-in page if they're not logged in).
 */

import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { verifyEmail } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { isLoggedIn, refreshUser } = useAuth();
  const [state, setState] = useState('verifying'); // verifying | success | error
  const [message, setMessage] = useState('');

  useEffect(() => {
    const uid = params.get('uid');
    const token = params.get('token');
    if (!uid || !token) {
      setState('error');
      setMessage('Verification link is missing required parameters.');
      return;
    }

    (async () => {
      try {
        await verifyEmail({ uid, token });
        if (isLoggedIn) await refreshUser();
        setState('success');
        setMessage('Email verified.');
      } catch (err) {
        setState('error');
        setMessage(err.message);
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto text-center">
        <h1 className="text-3xl font-bold mb-4"
            style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          {state === 'verifying' ? 'Verifying…'
            : state === 'success' ? 'Email verified'
            : 'Verification failed'}
        </h1>
        <p className="text-sm mb-8" style={{ color: 'var(--text-secondary)' }}>
          {state === 'verifying' ? 'Checking your link…' : message}
        </p>
        {state !== 'verifying' && (
          <Button onClick={() => navigate(isLoggedIn ? '/app/home' : '/sign-in')}>
            {isLoggedIn ? 'Go to app' : 'Sign in'}
          </Button>
        )}
      </div>
    </AuthShell>
  );
}
