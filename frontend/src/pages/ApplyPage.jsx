import { useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import { getOpportunity, applyToOpportunity } from '../api/opportunities';
import { generateCoverLetter } from '../api/talents';
import { uploadToSupabase } from '../api/uploads';
import { Button, PageHeader, CompanyLogo } from '../components/UI';
import { Upload } from 'lucide-react';

export default function ApplyPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isTalent } = useAuth();
  const { data: op, loading } = useApi(() => getOpportunity(id), [id]);

  const [coverLetter, setCoverLetter] = useState('');
  const [resumeUrl, setResumeUrl] = useState('');
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [resumeUploading, setResumeUploading] = useState(false);
  const [resumeError, setResumeError] = useState('');
  const resumeFileRef = useRef(null);
  
  const [draftingCoverLetter, setDraftingCoverLetter] = useState(false);
  
  const handleDraftCoverLetter = async () => {
    if (!id) return;
    setDraftingCoverLetter(true);
    setError('');
    try {
      const res = await generateCoverLetter(id);
      if (res?.data?.cover_letter) {
        setCoverLetter(res.data.cover_letter);
      } else {
        setError('Unexpected response from AI.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setDraftingCoverLetter(false);
    }
  };

  const handleResumePick = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setResumeUploading(true); setResumeError('');
    try {
      const url = await uploadToSupabase(file, 'resume');
      setResumeUrl(url);
    } catch (err) {
      setResumeError(err.message);
    } finally {
      setResumeUploading(false);
      if (resumeFileRef.current) resumeFileRef.current.value = '';
    }
  };

  const companyName = op?.organization?.name || 'SkillBridge';
  const companyKey = companyName.toLowerCase().replace(/\s/g, '');

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    try {
      await applyToOpportunity(id, {
        cover_letter: coverLetter,
        resume_url: resumeUrl,
        additional_notes: additionalNotes,
      });
      navigate(`/app/jobs/${id}/apply/success`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Loading…</p></div>;

  // Applications are talent-only. Mentors / org admins browse read-only.
  if (!isTalent) {
    return (
      <div className="p-8 max-w-2xl">
        <PageHeader title="Apply" onBack />
        <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: 'var(--border)' }}>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Only talents can apply to opportunities. Switch to a talent account to apply.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl">
      <PageHeader title="Apply Now" onBack />

      {/* Job summary */}
      <div className="bg-white rounded-2xl p-4 flex items-center gap-3 mb-6 border" style={{ borderColor: 'var(--border)' }}>
        <CompanyLogo companyKey={companyKey} size={44} />
        <div>
          <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{op?.title}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{companyName} · {op?.location || (op?.is_remote ? 'Remote' : 'On-site')}</p>
        </div>
      </div>

      {/* Resume URL */}
      <div className="mb-5">
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Resume / CV</p>
        <div className="flex gap-2 items-stretch">
          <input
            placeholder="Paste a link, or upload a PDF below"
            value={resumeUrl}
            onChange={e => setResumeUrl(e.target.value)}
            className="flex-1 px-4 py-3 rounded-2xl text-sm border"
            style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
          />
          <input ref={resumeFileRef} type="file" accept="application/pdf"
                 className="hidden" onChange={handleResumePick} />
          <button onClick={() => resumeFileRef.current?.click()} disabled={resumeUploading}
                  className="flex items-center gap-1 px-3 rounded-2xl text-sm font-medium border whitespace-nowrap disabled:opacity-50"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
            <Upload size={14} /> {resumeUploading ? 'Uploading…' : 'Upload PDF'}
          </button>
        </div>
        {resumeError && (
          <p className="text-xs mt-1.5" style={{ color: 'var(--red)' }}>{resumeError}</p>
        )}
        <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
          Public link works too (Google Drive, Dropbox, …). PDF only for uploads, max 5MB.
        </p>
      </div>

      {/* Cover Letter */}
      <div className="mb-5">
        <div className="flex justify-between items-center mb-2">
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            Cover Letter <span style={{ color: 'var(--text-muted)' }}>(optional)</span>
          </p>
          <button onClick={handleDraftCoverLetter} disabled={draftingCoverLetter} className="text-xs font-semibold flex items-center gap-1 disabled:opacity-50" style={{ color: 'var(--text-primary)' }}>
            <img src="/icons/star.svg" className="w-3 h-3" alt="AI" /> {draftingCoverLetter ? 'Drafting...' : 'Draft with AI'}
          </button>
        </div>
        <textarea
          placeholder="Tell the employer why you're the right fit for this role..."
          value={coverLetter}
          onChange={e => setCoverLetter(e.target.value)}
          rows={5}
          className="w-full px-4 py-3 rounded-2xl text-sm border resize-none"
          style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
        />
      </div>

      {/* Additional Notes */}
      <div className="mb-8">
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
          Additional Notes <span style={{ color: 'var(--text-muted)' }}>(optional)</span>
        </p>
        <textarea
          placeholder="Anything else you'd like the employer to know..."
          value={additionalNotes}
          onChange={e => setAdditionalNotes(e.target.value)}
          rows={3}
          className="w-full px-4 py-3 rounded-2xl text-sm border resize-none"
          style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
        />
      </div>

      {error && <p className="text-sm mb-4 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

      <Button onClick={handleSubmit} disabled={submitting}>
        {submitting ? 'Submitting…' : 'Submit Application'}
      </Button>
    </div>
  );
}
