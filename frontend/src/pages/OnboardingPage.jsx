import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { onboardingSlides } from '../data';
import { Button } from '../components/UI';

export default function OnboardingPage() {
  const [current, setCurrent] = useState(0);
  const navigate = useNavigate();
  const slide = onboardingSlides[current];
  const isLast = current === onboardingSlides.length - 1;

  const next = () => {
    if (isLast) navigate('/create-account');
    else setCurrent(c => c + 1);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-between py-16 px-6" style={{ background: 'var(--bg)' }}>
      {/* Skip */}
      <div className="self-end">
        <button onClick={() => navigate('/create-account')} className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Skip
        </button>
      </div>

      {/* Illustration placeholder */}
      <div
        className="w-64 h-64 rounded-3xl flex items-center justify-center"
        style={{ background: '#E5E4E0' }}
      >
        <img src="/logos/logo.svg" className="w-20 h-20 opacity-30 object-contain" alt="SkillBridge Logo" />
      </div>

      {/* Text */}
      <div className="text-center max-w-xs">
        <h2 className="text-2xl font-bold mb-3" style={{ color: 'var(--text-primary)', fontFamily: "'DM Serif Display', serif" }}>
          {slide.title}
        </h2>
        <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {slide.subtitle}
        </p>
      </div>

      {/* Dots + Button */}
      <div className="w-full max-w-xs">
        <div className="flex justify-center gap-2 mb-6">
          {onboardingSlides.map((_, i) => (
            <div
              key={i}
              onClick={() => setCurrent(i)}
              className="rounded-full cursor-pointer transition-all"
              style={{
                width: i === current ? 24 : 8,
                height: 8,
                background: i === current ? 'var(--text-primary)' : '#D1D0CC',
              }}
            />
          ))}
        </div>
        <Button onClick={next}>
          {isLast ? 'Get Started' : 'Next'}
        </Button>
      </div>
    </div>
  );
}
