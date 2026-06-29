import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/UI';

export default function ApplicationSuccessPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center" style={{ background: 'var(--bg)' }}>
      <div className="w-24 h-24 rounded-full flex items-center justify-center mb-6" style={{ background: '#D1FAE5' }}>
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" fill="#16A34A"/>
          <path d="M8 12L11 15L16 9" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <h1 className="text-3xl font-bold mb-3" style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
        Application Sent!
      </h1>
      <p className="text-sm mb-10 max-w-xs" style={{ color: 'var(--text-secondary)' }}>
        Your application has been submitted successfully. You'll be notified when there's an update.
      </p>
      <div className="w-full max-w-xs flex flex-col gap-3">
        <Button onClick={() => navigate('/app/home')}>Back to Home</Button>
        <Button variant="secondary" onClick={() => navigate('/app/notifications')}>View Applications</Button>
      </div>
    </div>
  );
}
