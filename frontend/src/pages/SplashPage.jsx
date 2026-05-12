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
        <svg width="64" height="64" viewBox="0 0 40 40" fill="none">
          <path d="M20 6C12 6 6 11 6 18C6 23 10 27 15 28L20 35L25 28C30 27 34 23 34 18C34 11 28 6 20 6Z" fill="#1A1A1A"/>
          <path d="M13 19C13 19 16 23 20 23C24 23 27 19 27 19" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
        <div className="text-center">
          <h1 className="text-3xl font-semibold" style={{ color: 'var(--text-primary)' }}>SkillBridge</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Version 1.0</p>
        </div>
      </div>
    </div>
  );
}
