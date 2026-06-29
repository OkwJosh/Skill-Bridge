import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AuthShell, Button, Input } from '../components/UI';
import { Eye, EyeOff } from 'lucide-react';
import { confirmPasswordReset } from '../api/auth';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const uid = searchParams.get('uid') || '';
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirm, setConfirm]   = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [done, setDone]         = useState(false);
  const [error, setError]       = useState('');

  const handleSubmit = async () => {
    if (!uid || !token) {
      setError('Invalid reset link. Request a new one.');
      return;
    }
    if (password.length < 6) { setError('Password must be at least 6 characters.'); return; }
    if (password !== confirm)  { setError('Passwords do not match.'); return; }

    setLoading(true); setError('');
    try {
      await confirmPasswordReset({ uid, token, new_password: password });
      setDone(true);
    } catch (err) {
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
          Reset<br />password
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          {done ? 'Password updated. You can now sign in.' : 'Choose a new password for your account.'}
        </p>

        {!done && (
          <>
            <div className="flex flex-col gap-3 mb-2">
              <Input placeholder="New password"
                     type={showPass ? 'text' : 'password'}
                     value={password}
                     onChange={e => setPassword(e.target.value)}
                     rightIcon={
                       <button onClick={() => setShowPass(s => !s)}>
                         {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                       </button>
                     } />
              <Input placeholder="Confirm new password"
                     type={showPass ? 'text' : 'password'}
                     value={confirm}
                     onChange={e => setConfirm(e.target.value)} />
            </div>
            {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}
            <Button onClick={handleSubmit} disabled={loading} className="mb-4">
              {loading ? 'Updating…' : 'Update password'}
            </Button>
          </>
        )}

        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }}
                onClick={() => navigate('/sign-in')}>
            {done ? 'Sign in' : 'Back to sign in'}
          </span>
        </p>
      </div>
    </AuthShell>
  );
}
