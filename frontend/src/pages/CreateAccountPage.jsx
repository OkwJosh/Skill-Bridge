import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button, Input } from '../components/UI';
import { Eye, EyeOff } from 'lucide-react';

export default function CreateAccountPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = () => navigate('/verification');

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center" style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          Create<br />account
        </h1>

        <div className="flex flex-col gap-3 mb-4">
          <Input
            placeholder="Email address"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <Input
            placeholder="Password"
            type={showPass ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            rightIcon={
              <button onClick={() => setShowPass(s => !s)}>
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
          />
        </div>

        <Button onClick={handleSubmit} className="mb-4">Create account</Button>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>or sign up with</span>
          <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        </div>

        <div className="flex justify-center gap-4 mb-6">
          {['G', '🍎', 'f'].map((icon, i) => (
            <button key={i} className="w-12 h-12 rounded-full border flex items-center justify-center hover:bg-gray-50 text-lg" style={{ borderColor: 'var(--border)' }}>
              {icon}
            </button>
          ))}
        </div>

        <p className="text-xs text-center mb-6" style={{ color: 'var(--text-muted)' }}>
          By creating an account you agree to SkillBridge's{' '}
          <span className="underline cursor-pointer" style={{ color: 'var(--text-primary)' }}>Terms of Services</span>
          {' '}and{' '}
          <span className="underline cursor-pointer" style={{ color: 'var(--text-primary)' }}>Privacy Policy</span>.
        </p>

        <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>
          Have an account?{' '}
          <span className="font-bold cursor-pointer" style={{ color: 'var(--text-primary)' }} onClick={() => navigate('/sign-in')}>
            Log in
          </span>
        </p>
      </div>
    </AuthShell>
  );
}
