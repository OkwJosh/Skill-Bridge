import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';

export function VerificationPage() {
  const navigate = useNavigate();
  const [code, setCode] = useState(['', '', '', '', '', '']);

  const handleChange = (i, val) => {
    if (val.length > 1) return;
    const next = [...code];
    next[i] = val;
    setCode(next);
    if (val && i < 5) document.getElementById(`otp-${i + 1}`)?.focus();
  };

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center" style={{ fontFamily: "'DM Serif Display', serif" }}>
          Verify your<br />email
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          We sent a 6-digit code to your email address. Please enter it below.
        </p>

        <div className="flex gap-3 justify-center mb-8">
          {code.map((c, i) => (
            <input
              key={i}
              id={`otp-${i}`}
              value={c}
              onChange={e => handleChange(i, e.target.value)}
              maxLength={1}
              className="w-12 h-12 text-center text-lg font-bold rounded-xl border"
              style={{
                background: '#F9F9F7',
                borderColor: c ? 'var(--text-primary)' : 'var(--border)',
              }}
            />
          ))}
        </div>

        <Button onClick={() => navigate('/about-you')} className="mb-4">Verify</Button>
        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          Didn't receive a code?{' '}
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }}>Resend</span>
        </p>
      </div>
    </AuthShell>
  );
}

export default VerificationPage;
