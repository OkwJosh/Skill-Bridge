import { useNavigate, useParams } from 'react-router-dom';
import { jobs } from '../data';
import { Button, CompanyLogo } from '../components/UI';

export default function ApplicationSuccessPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const job = jobs.find(j => j.id === Number(id)) || jobs[0];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-8 text-center" style={{ background: 'var(--bg)' }}>
      {/* Big success checkmark */}
      <div className="w-28 h-28 rounded-full flex items-center justify-center mb-6" style={{ background: '#D1FAE5' }}>
        <svg width="52" height="52" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" fill="#16A34A" />
          <path d="M7.5 12L10.5 15L16.5 9" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
        Application Sent!
      </h1>
      <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
        Your application for
      </p>

      <div className="flex items-center gap-2 mb-2">
        <CompanyLogo companyKey={job.companyKey} size={28} />
        <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{job.title} at {job.company}</span>
      </div>

      <p className="text-sm mb-10 max-w-xs" style={{ color: 'var(--text-secondary)' }}>
        has been successfully submitted. We'll notify you of any updates.
      </p>

      <div className="w-full max-w-xs flex flex-col gap-3">
        <Button onClick={() => navigate('/app/home')}>Back to Home</Button>
        <Button variant="secondary" onClick={() => navigate('/app/jobs')}>Browse More Jobs</Button>
      </div>
    </div>
  );
}
