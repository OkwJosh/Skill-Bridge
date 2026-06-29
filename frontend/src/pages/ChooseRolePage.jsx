/**
 * ChooseRolePage — shown right after first-time OAuth sign-up.
 *
 * The backend creates an OAuth-signed-up user with NO role flag set, so
 * `user.needs_onboarding === true`. This page lets the user pick one and
 * PATCHes /auth/me/ to apply it, then routes them into the app.
 *
 * Email/password signups already pick a role at /create-account and skip this.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { useAuth } from '../context/AuthContext';
import { updateMe } from '../api/auth';

const ROLES = [
  { key: 'is_talent',       label: 'Talent',       desc: 'Find opportunities and build a portfolio.' },
  { key: 'is_mentor',       label: 'Mentor',       desc: 'Run guided projects and endorse skills.' },
  { key: 'is_org_admin',    label: 'Organization', desc: 'Post opportunities and find talent.' },
  { key: 'is_school_admin', label: 'School',       desc: 'Verify academic records for your students.' },
];

export default function ChooseRolePage() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleContinue = async () => {
    if (!selected) { setError('Pick a role to continue.'); return; }
    setLoading(true); setError('');
    try {
      await updateMe({ [selected]: true });
      await refreshUser();
      // Talents land in the existing about-you onboarding chain.
      // Org admins set up their org. School admins register their school.
      // Mentors land in the app and can fill profile later.
      const next =
        selected === 'is_talent'       ? '/about-you'
      : selected === 'is_org_admin'    ? '/create-organization'
      : selected === 'is_school_admin' ? '/create-school'
      : '/app/home';
      navigate(next, { replace: true });
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
          How will you<br />use SkillBridge?
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          You can change or add roles later from settings.
        </p>

        <div className="flex flex-col gap-3 mb-6">
          {ROLES.map((r) => (
            <button key={r.key}
                    onClick={() => setSelected(r.key)}
                    className="text-left p-4 rounded-2xl border transition"
                    style={{
                      borderColor: selected === r.key ? 'var(--text-primary)' : 'var(--border)',
                      background: selected === r.key ? '#F9F9F7' : 'white',
                    }}>
              <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{r.label}</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{r.desc}</p>
            </button>
          ))}
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleContinue} disabled={loading || !selected}>
          {loading ? 'Saving…' : 'Continue'}
        </Button>
      </div>
    </AuthShell>
  );
}
