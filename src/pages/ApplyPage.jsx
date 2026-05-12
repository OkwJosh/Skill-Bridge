import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { jobs } from '../data';
import { Button, PageHeader, CompanyLogo } from '../components/UI';
import { Upload } from 'lucide-react';

export default function ApplyPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const job = jobs.find(j => j.id === Number(id)) || jobs[0];
  const [coverLetter, setCoverLetter] = useState('');
  const [cvUploaded, setCvUploaded] = useState(false);

  return (
    <div className="p-8 max-w-2xl">
      <PageHeader title="Apply Now" onBack />

      {/* Job summary */}
      <div className="bg-white rounded-2xl p-4 flex items-center gap-3 mb-6 border" style={{ borderColor: 'var(--border)' }}>
        <CompanyLogo companyKey={job.companyKey} size={44} />
        <div>
          <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{job.title}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{job.company} · {job.location}</p>
        </div>
      </div>

      {/* CV Upload */}
      <div className="mb-5">
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Upload CV / Resume</p>
        <button
          onClick={() => setCvUploaded(true)}
          className="w-full border-2 border-dashed rounded-2xl p-8 flex flex-col items-center gap-2 hover:bg-gray-50 transition-colors"
          style={{ borderColor: cvUploaded ? 'var(--text-primary)' : 'var(--border)' }}
        >
          <Upload size={24} style={{ color: cvUploaded ? 'var(--text-primary)' : 'var(--text-muted)' }} />
          <p className="text-sm font-medium" style={{ color: cvUploaded ? 'var(--text-primary)' : 'var(--text-muted)' }}>
            {cvUploaded ? 'resume.pdf — uploaded ✓' : 'Click to upload your CV'}
          </p>
          {!cvUploaded && <p className="text-xs" style={{ color: 'var(--text-muted)' }}>PDF, DOC up to 10MB</p>}
        </button>
      </div>

      {/* Cover Letter */}
      <div className="mb-8">
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Cover Letter <span style={{ color: 'var(--text-muted)' }}>(optional)</span></p>
        <textarea
          placeholder="Tell the employer why you're the right fit for this role..."
          value={coverLetter}
          onChange={e => setCoverLetter(e.target.value)}
          rows={5}
          className="w-full px-4 py-3 rounded-2xl text-sm border resize-none"
          style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
        />
      </div>

      <Button onClick={() => navigate(`/app/jobs/${job.id}/apply/success`)}>
        Submit Application
      </Button>
    </div>
  );
}
