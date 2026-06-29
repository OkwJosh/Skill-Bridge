import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Share2, Users, Clock, MapPin, Bookmark } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import { getOpportunity } from '../api/opportunities';
import { CompanyLogo, Button, PageHeader } from '../components/UI';

const tabs = ['Overview', 'Requirements', 'About'];

const TYPE_LABELS = {
  internship: 'Internship',
  micro_project: 'Micro-Project',
  guided_project: 'Guided Project',
};

export default function JobDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isTalent } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [saved, setSaved] = useState(false);

  const { data: op, loading, error } = useApi(() => getOpportunity(id), [id]);

  if (loading) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Loading…</p></div>;
  if (error) return <div className="p-8"><p style={{ color: 'var(--red)' }}>Error: {error}</p></div>;
  if (!op) return null;

  const companyName = op.organization?.name || 'SkillBridge';
  const companyKey = companyName.toLowerCase().replace(/\s/g, '');
  const location = op.location || (op.is_remote ? 'Remote' : 'On-site');
  const deadline = op.application_deadline
    ? new Date(op.application_deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    : 'Open';
  const daysLeft = op.application_deadline
    ? Math.max(0, Math.ceil((new Date(op.application_deadline) - Date.now()) / 86400000))
    : null;

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader title="Opportunity Details" onBack rightSlot={
        <button className="w-9 h-9 rounded-full border flex items-center justify-center hover:bg-gray-50" style={{ borderColor: 'var(--border)' }}>
          <Share2 size={16} />
        </button>
      } />

      <div className="flex gap-6">
        <div className="flex-1 min-w-0">
          {/* Hero */}
          <div className="rounded-2xl p-8 text-center mb-6" style={{ background: 'var(--text-primary)' }}>
            <div className="flex justify-center mb-3">
              <CompanyLogo companyKey={companyKey} size={56} />
            </div>
            <h2 className="text-xl font-bold text-white mb-1">{op.title}</h2>
            <p className="text-sm mb-1" style={{ color: '#9CA3AF' }}>{companyName}</p>
            <p className="text-sm mb-3" style={{ color: '#9CA3AF' }}>
              {TYPE_LABELS[op.opportunity_type] || op.opportunity_type} · {op.is_remote ? 'Remote' : 'Onsite'}
            </p>
            <p className="text-lg font-bold text-white">
              {op.compensation || (op.is_paid ? 'Paid' : 'Unpaid')}
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              { icon: <Users size={16} />, label: `${op.applicant_count ?? 0} Applicants` },
              { icon: <Clock size={16} />, label: daysLeft !== null ? `${daysLeft} Days Left` : 'Open' },
              { icon: <MapPin size={16} />, label: location },
            ].map((stat, i) => (
              <div key={i} className="bg-white rounded-xl p-3 flex flex-col items-center gap-1 border" style={{ borderColor: 'var(--border)' }}>
                <span style={{ color: 'var(--text-muted)' }}>{stat.icon}</span>
                <span className="text-xs text-center" style={{ color: 'var(--text-secondary)' }}>{stat.label}</span>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div className="flex border-b mb-6" style={{ borderColor: 'var(--border)' }}>
            {tabs.map((tab, i) => (
              <button key={i} onClick={() => setActiveTab(i)}
                className="mr-6 pb-3 text-sm font-medium relative"
                style={{ color: activeTab === i ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                {tab}
                {activeTab === i && <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" style={{ background: 'var(--text-primary)' }} />}
              </button>
            ))}
          </div>

          {activeTab === 0 && (
            <div>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>📋 Description</h3>
              <p className="text-sm leading-relaxed mb-5 whitespace-pre-line" style={{ color: 'var(--text-secondary)' }}>{op.description}</p>
              {op.duration && <p className="text-sm" style={{ color: 'var(--text-secondary)' }}><strong>Duration:</strong> {op.duration}</p>}
              {op.spots_available && <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}><strong>Spots:</strong> {op.spots_available}</p>}
              <div className="flex justify-between items-center mt-6 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
                <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Deadline</span>
                <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{deadline}</span>
              </div>
            </div>
          )}

          {activeTab === 1 && (
            <div>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Required Skills</h3>
              <div className="flex flex-wrap gap-2 mb-4">
                {(op.required_skills || []).map(s => (
                  <span key={s.id} className="px-3 py-1 rounded-full text-xs font-medium" style={{ background: '#F3F4F6', color: 'var(--text-secondary)' }}>
                    {s.name}
                  </span>
                ))}
                {(!op.required_skills || op.required_skills.length === 0) && (
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No specific skills listed.</p>
                )}
              </div>
              {op.experience_level && (
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  <strong>Experience level:</strong> {op.experience_level}
                </p>
              )}
            </div>
          )}

          {activeTab === 2 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <CompanyLogo companyKey={companyKey} size={48} />
                <div>
                  <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{companyName}</p>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{op.organization?.city || location}</p>
                </div>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {op.organization?.description || 'No company description available.'}
              </p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-64 shrink-0">
          <div className="bg-white rounded-2xl p-5 border sticky top-6" style={{ borderColor: 'var(--border)' }}>
            <p className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Interested in this role?</p>
            <div className="flex flex-col gap-3 mb-5">
              {[
                { label: 'Pay', value: op.compensation || (op.is_paid ? 'Paid' : 'Unpaid') },
                { label: 'Type', value: TYPE_LABELS[op.opportunity_type] || op.opportunity_type },
                { label: 'Mode', value: op.is_remote ? 'Remote' : 'Onsite' },
                { label: 'Deadline', value: deadline },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                  <span className="font-medium capitalize" style={{ color: 'var(--text-primary)' }}>{value}</span>
                </div>
              ))}
            </div>
            {/* Only talents can apply. Mentors / org admins browse read-only. */}
            {isTalent ? (
              <Button onClick={() => navigate(`/app/jobs/${id}/apply`)} className="mb-3">Apply Now</Button>
            ) : (
              <p className="text-xs mb-3 px-1" style={{ color: 'var(--text-muted)' }}>
                Applications are open to talents only.
              </p>
            )}
            <Button variant="secondary" onClick={() => setSaved(s => !s)}>
              <span className="flex items-center justify-center gap-2">
                <Bookmark size={16} fill={saved ? 'currentColor' : 'none'} />
                {saved ? 'Saved' : 'Save'}
              </span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
