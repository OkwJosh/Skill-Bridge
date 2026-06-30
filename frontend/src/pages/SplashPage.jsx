import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SplashPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const t = setTimeout(() => navigate('/onboarding'), 2000);
    return () => clearTimeout(t);
  }, [navigate]);

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center"
      style={{ background: 'var(--bg)' }}
    >
      <div className="flex flex-col items-center gap-4 animate-pulse">
        <img src="/logos/logo.svg" className="w-16 h-16 object-contain" alt="SkillBridge Logo" />
        <div className="text-center">
          <h1 className="text-3xl font-semibold" style={{ color: 'var(--text-primary)' }}>SkillBridge</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Version 1.0</p>
        </div>
      </div>
    </div>
  );
}
