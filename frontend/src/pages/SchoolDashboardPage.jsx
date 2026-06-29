import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, RefreshCw, ExternalLink, Users } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import { getMySchool } from '../api/schools';
import { getCurriculumAlignment } from '../api/ai';

export default function SchoolDashboardPage() {
  const navigate = useNavigate();
  const { data: school, loading, error } = useApi(getMySchool);

  // If the school_admin hasn't registered their school yet, send them
  // to /create-school instead of showing a 404. Mirrors OrgProfilePage.
  useEffect(() => {
    if (error && /no_school|not assigned to any school/i.test(error)) {
      navigate('/create-school', { replace: true });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error]);

  const isMissingSchool = error && /no_school|not assigned to any school/i.test(error);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
        {school?.name || 'School Dashboard'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
        {school?.school_type ? `${school.school_type} · ` : ''}
        {[school?.city, school?.state, school?.country].filter(Boolean).join(', ')}
      </p>

      {loading && <p style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && !isMissingSchool && <p style={{ color: 'var(--red)' }}>{error}</p>}

      {school && (
        <>
          {/* Quick actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <ActionCard
              icon={Users}
              title="Student Roster"
              desc="Manage students you've consented to verify."
              onClick={() => navigate('/app/school/roster')}
            />
            {school.website_url && (
              <a href={school.website_url} target="_blank" rel="noopener noreferrer"
                 className="bg-white rounded-2xl p-5 border block hover:shadow-md transition-shadow"
                 style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <ExternalLink size={16} style={{ color: 'var(--text-secondary)' }} />
                  <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                    School website
                  </p>
                </div>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{school.website_url}</p>
              </a>
            )}
          </div>

          {/* AI Curriculum Alignment */}
          <CurriculumAlignmentCard schoolId={school.id} />
        </>
      )}
    </div>
  );
}

function ActionCard({ icon: Icon, title, desc, onClick }) {
  return (
    <button onClick={onClick}
            className="bg-white rounded-2xl p-5 border text-left hover:shadow-md transition-shadow"
            style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-1">
        <Icon size={16} style={{ color: 'var(--text-secondary)' }} />
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</p>
      </div>
      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{desc}</p>
    </button>
  );
}

function CurriculumAlignmentCard({ schoolId }) {
  const { data, loading, error, aiDisabled, refresh } = useAIInsight(
    ({ refresh } = {}) => getCurriculumAlignment(schoolId, { refresh }),
    [schoolId],
  );
  if (aiDisabled) return null;
  const p = data?.payload;

  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} style={{ color: 'var(--text-secondary)' }} />
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Curriculum-to-Market Alignment (AI)
          </p>
        </div>
        <button onClick={refresh} title="Refresh">
          <RefreshCw size={14} style={{ color: 'var(--text-muted)' }} />
        </button>
      </div>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Generating report…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {p && (
        <>
          {p.summary && (
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>{p.summary}</p>
          )}

          <div className="grid grid-cols-3 gap-3 mb-4 text-center">
            <Stat label="Departments" value={p.departments?.length ?? 0} />
            <Stat label="Verified graduates" value={p.graduate_count ?? 0} />
            <Stat label="Skills in demand" value={p.market_demand?.length ?? 0} />
          </div>

          {(p.underrepresented_skills?.length > 0) && (
            <div className="mb-4">
              <p className="text-xs font-semibold mb-2 uppercase tracking-wide"
                 style={{ color: 'var(--text-muted)' }}>
                Under-represented skills
              </p>
              <div className="flex flex-col gap-2">
                {p.underrepresented_skills.map((s, i) => (
                  <div key={i} className="border rounded-lg p-3" style={{ borderColor: 'var(--border)' }}>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{s.skill}</span>
                      <span style={{ color: 'var(--text-muted)' }}>
                        {s.current_graduates_with_skill} / {s.market_demand} jobs
                      </span>
                    </div>
                    {s.recommendation && (
                      <p className="text-xs mt-1 italic" style={{ color: 'var(--text-secondary)' }}>
                        {s.recommendation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {(p.well_aligned_departments?.length > 0) && (
            <div>
              <p className="text-xs font-semibold mb-2 uppercase tracking-wide"
                 style={{ color: 'var(--text-muted)' }}>
                Well-aligned departments
              </p>
              <ul className="text-sm list-disc pl-5" style={{ color: 'var(--text-secondary)' }}>
                {p.well_aligned_departments.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</p>
      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</p>
    </div>
  );
}
