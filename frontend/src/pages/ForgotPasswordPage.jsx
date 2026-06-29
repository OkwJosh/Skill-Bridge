import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button, Input } from '../components/UI';
import { requestPasswordReset } from '../api/auth';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!email) { setError('Please enter your email.'); return; }
    setLoading(true); setError('');
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (err) {
      // Backend always 200s for security; an error here is genuinely a network issue.
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center"
            style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          Forgot<br />password?
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          {sent
            ? "If an account with that email exists, we've sent a reset link."
            : "Enter your email and we'll send you a link to reset your password."}
        </p>

        {!sent && (
          <>
            <div className="flex flex-col gap-3 mb-2">
              <Input placeholder="Email address" type="email"
                     value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}
            <Button onClick={handleSubmit} disabled={loading} className="mb-4">
              {loading ? 'Sending…' : 'Send reset link'}
            </Button>
          </>
        )}

        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }}
                onClick={() => navigate('/sign-in')}>
            Back to sign in
          </span>
        </p>
      </div>
    </AuthShell>
  );
}
