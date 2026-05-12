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
        <svg width="80" height="80" viewBox="0 0 40 40" fill="none">
          <path d="M20 6C12 6 6 11 6 18C6 23 10 27 15 28L20 35L25 28C30 27 34 23 34 18C34 11 28 6 20 6Z" fill="#1A1A1A" opacity="0.3"/>
        </svg>
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
