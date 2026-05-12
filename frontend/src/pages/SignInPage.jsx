import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button, Input } from '../components/UI';
import { Eye, EyeOff } from 'lucide-react';

export default function SignInPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [remember, setRemember] = useState(false);

  const handleLogin = () => navigate('/app/home');

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center" style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          Welcome<br />back
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          Log in to find new opportunities waiting for you.
        </p>

        <div className="flex flex-col gap-3 mb-2">
          <Input placeholder="Email address" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          <Input
            placeholder="Password"
            type={showPass ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            rightIcon={<button onClick={() => setShowPass(s => !s)}>{showPass ? <EyeOff size={16} /> : <Eye size={16} />}</button>}
          />
        </div>

        <div className="flex justify-between items-center mb-5">
          <label className="flex items-center gap-2 text-sm cursor-pointer" style={{ color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} className="rounded" />
            Remember Me
          </label>
          <button className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Forgot Password?</button>
        </div>

        <Button onClick={handleLogin} className="mb-4">Log in</Button>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>or sign in with</span>
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        </div>

        <div className="flex justify-center gap-4 mb-6">
          {['G', '🍎', 'f'].map((icon, i) => (
            <button key={i} className="w-12 h-12 rounded-full border flex items-center justify-center hover:bg-gray-50 text-lg" style={{ borderColor: 'var(--border)' }}>
              {icon}
            </button>
          ))}
        </div>

        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          Don't have an account?{' '}
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }} onClick={() => navigate('/create-account')}>
            Sign Up
          </span>
        </p>
      </div>
    </AuthShell>
  );
}
