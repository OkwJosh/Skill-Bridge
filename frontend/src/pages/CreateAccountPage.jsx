import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button, Input } from '../components/UI';
import OAuthButtons from '../components/OAuthButtons';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// User picks role explicitly on signup. No silent default.
const ROLES = [
  { key: 'talent',       label: 'Talent',       desc: 'Find opportunities and build a portfolio.' },
  { key: 'mentor',       label: 'Mentor',       desc: 'Run guided projects and endorse skills.' },
  { key: 'org_admin',    label: 'Organization', desc: 'Post opportunities and find talent.' },
  { key: 'school_admin', label: 'School',       desc: 'Verify academic records for your students.' },
];

export default function CreateAccountPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [role, setRole]         = useState('talent');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone]       = useState('');
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');

  const handleSubmit = async () => {
    if (!fullName.trim()) { setError('Please enter your full name.'); return; }
    if (!email || !password) { setError('Email and password are required.'); return; }
    if (password.length < 6)  { setError('Password must be at least 6 characters.'); return; }
    setLoading(true); setError('');
    try {
      const user = await register({
        email,
        password,
        role,
        full_name: fullName.trim(),
        phone_number: phone.trim(),
      });
      // Route based on role:
      //   talent       → continue talent onboarding (about-you → add-skills)
      //   org_admin    → org setup (creates Organization + OrganizationMember)
      //   school_admin → school setup (creates School + adds caller as admin)
      //   mentor       → land in the app; can fill profile from Settings
      const path =
        user.is_talent       ? '/about-you'
      : user.is_org_admin    ? '/create-organization'
      : user.is_school_admin ? '/create-school'
      : '/app/home';
      navigate(path, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center"
            style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          Create<br />account
        </h1>

        {/* Role picker */}
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>I am a…</p>
        <div className="flex flex-col gap-2 mb-5">
          {ROLES.map((r) => (
            <button key={r.key}
                    type="button"
                    onClick={() => setRole(r.key)}
                    className="text-left p-3 rounded-2xl border transition"
                    style={{
                      borderColor: role === r.key ? 'var(--text-primary)' : 'var(--border)',
                      background: role === r.key ? '#F9F9F7' : 'white',
                    }}>
              <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{r.label}</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{r.desc}</p>
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-3 mb-2">
          <Input placeholder="Full name" value={fullName} onChange={e => setFullName(e.target.value)} />
          <Input placeholder="Phone number (optional)" type="tel"
                 value={phone} onChange={e => setPhone(e.target.value)} />
          <Input placeholder="Email address" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          <Input placeholder="Password"
                 type={showPass ? 'text' : 'password'}
                 value={password}
                 onChange={e => setPassword(e.target.value)}
                 rightIcon={
                   <button type="button" onClick={() => setShowPass(s => !s)}>
                     {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                   </button>
                 } />
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleSubmit} disabled={loading} className="mb-4">
          {loading ? 'Creating account…' : 'Create account'}
        </Button>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>or sign up with</span>
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        </div>

        <OAuthButtons onError={setError} />

        <p className="text-xs text-center mb-6" style={{ color: 'var(--text-muted)' }}>
          By creating an account you agree to SkillBridge's{' '}
          <span className="underline cursor-pointer" style={{ color: 'var(--text-primary)' }}>Terms of Services</span>
          {' '}and{' '}
          <span className="underline cursor-pointer" style={{ color: 'var(--text-primary)' }}>Privacy Policy</span>.
        </p>

        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          Have an account?{' '}
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }} onClick={() => navigate('/sign-in')}>Log in</span>
        </p>
      </div>
    </AuthShell>
  );
}
