import { useParams, useNavigate } from 'react-router-dom';
import { Mail, ExternalLink, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import { getTalentProfile } from '../api/talents';
import { getTalentTrustScore } from '../api/ai';
import { Avatar, PageHeader } from '../components/UI';

export default function TalentProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isOrgAdmin } = useAuth();

  const { data: talent, loading, error } = useApi(() => getTalentProfile(id), [id]);

  // AI Trust Score (any auth'd user can view)
  const { data: trustData, aiDisabled } = useAIInsight(
    ({ refresh } = {}) => getTalentTrustScore(id, { refresh }),
    [id],
  );

  if (loading) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Loading…</p></div>;
  if (error)   return <div className="p-8"><p style={{ color: 'var(--red)' }}>{error}</p></div>;
  if (!talent) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Not found.</p></div>;

  const name = talent.user?.full_name || talent.user?.email || '—';
  const location = [talent.city, talent.state, talent.country].filter(Boolean).join(', ');
  const score = trustData?.payload?.score;

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader title="Profile" onBack />

      <div className="flex gap-6 items-start">
        <div className="flex-1">
          <div className="flex flex-col items-center text-center mb-8">
            <Avatar name={name} size={80} className="mb-3" />
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{name}</h2>
            {talent.headline && (
              <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>{talent.headline}</p>
            )}
            {location && (
              <p className="text-sm mb-2" style={{ color: 'var(--text-muted)' }}>{location}</p>
            )}
            <div className="flex gap-2 mt-1">
              {talent.is_available && (
                <span className="text-xs font-medium px-3 py-1 rounded-full"
                      style={{ background: '#D1FAE5', color: '#065F46' }}>
                  Open to Work
                </span>
              )}
              {talent.is_school_verified && (
                <span className="text-xs font-medium px-3 py-1 rounded-full flex items-center gap-1"
                      style={{ background: '#DBEAFE', color: '#1E40AF' }}>
                  <ShieldCheck size={12} /> Verified
                </span>
              )}
            </div>
          </div>

          {talent.bio && (
            <section className="mb-6">
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>About</h3>
              <p className="text-sm leading-relaxed whitespace-pre-line"
                 style={{ color: 'var(--text-secondary)' }}>
                {talent.bio}
              </p>
            </section>
          )}

          <section className="mb-6">
            <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Skills</h3>
            <div className="flex flex-wrap gap-2">
              {(talent.skills || []).map(s => (
                <span key={s.skill?.id || s.id}
                      className="px-3 py-1.5 rounded-full text-xs font-medium border flex items-center gap-1"
                      style={{
                        background: s.is_endorsed ? '#D1FAE5' : 'var(--text-primary)',
                        color: s.is_endorsed ? '#065F46' : '#fff',
                        borderColor: s.is_endorsed ? '#065F46' : 'transparent',
                      }}>
                  {s.skill?.name}
                  {s.is_endorsed && <span title="Endorsed by mentor">✓</span>}
                </span>
              ))}
              {(talent.skills || []).length === 0 && (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No skills listed.</p>
              )}
            </div>
          </section>

          {talent.education_route && (
            <section className="mb-6">
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Education</h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {talent.field_of_study || '—'}
                {talent.institution_name && ` · ${talent.institution_name}`}
                {talent.graduation_year && ` · ${talent.graduation_year}`}
              </p>
            </section>
          )}

          {(talent.portfolio_url || talent.github_url || talent.linkedin_url) && (
            <section className="mb-6">
              <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Links</h3>
              <div className="flex flex-col gap-2">
                {talent.portfolio_url && (
                  <a href={talent.portfolio_url} target="_blank" rel="noopener noreferrer"
                     className="text-sm flex items-center gap-1 underline"
                     style={{ color: 'var(--text-primary)' }}>
                    Portfolio <ExternalLink size={12} />
                  </a>
                )}
                {talent.github_url && (
                  <a href={talent.github_url} target="_blank" rel="noopener noreferrer"
                     className="text-sm flex items-center gap-1 underline"
                     style={{ color: 'var(--text-primary)' }}>
                    GitHub <ExternalLink size={12} />
                  </a>
                )}
                {talent.linkedin_url && (
                  <a href={talent.linkedin_url} target="_blank" rel="noopener noreferrer"
                     className="text-sm flex items-center gap-1 underline"
                     style={{ color: 'var(--text-primary)' }}>
                    LinkedIn <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </section>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-64 shrink-0">
          {/* Trust Score */}
          {!aiDisabled && (
            <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-2 mb-3">
                <ShieldCheck size={16} style={{ color: 'var(--text-secondary)' }} />
                <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Trust Score</p>
              </div>
              {score !== undefined ? (
                <>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{score}</span>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>/ 100</span>
                  </div>
                  {trustData?.payload?.rationale && (
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {trustData.payload.rationale}
                    </p>
                  )}
                </>
              ) : (
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Computing…</p>
              )}
            </div>
          )}

          {/* Contact (org admins only) */}
          <div className="bg-white rounded-2xl p-5 border sticky top-8" style={{ borderColor: 'var(--border)' }}>
            <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
              Contact {name.split(' ')[0]}
            </p>
            {isOrgAdmin ? (
              <a href={`mailto:${talent.user?.email}`}
                 className="w-full inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-medium text-white"
                 style={{ background: 'var(--text-primary)' }}>
                <Mail size={15} /> Email
              </a>
            ) : (
              <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
                Only organization admins can contact talents directly.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
