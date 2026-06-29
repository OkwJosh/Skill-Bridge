import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, SlidersHorizontal, Plus, Sparkles, Users, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import { getOpportunities } from '../api/opportunities';
import { listTalents } from '../api/talents';
import { getMyOrganization } from '../api/organizations';
import { listMyMentorships, getMyMentorProfile } from '../api/mentors';
import { getProactiveSourcing } from '../api/ai';
import { JobCardSmall, JobCardWide, SectionHeader, Avatar } from '../components/UI';


// ─── Role router ────────────────────────────────────────────────────────────
export default function HomePage() {
  const { user, isTalent, isMentor, isOrgAdmin } = useAuth();
  const isSchoolAdmin = user?.is_school_admin;

  return (
    <div className="p-8 max-w-5xl">
      <Header user={user} />
      {isTalent     && <TalentHome />}
      {isMentor     && <MentorHome />}
      {isOrgAdmin   && <OrgHome />}
      {isSchoolAdmin && <SchoolHome />}
      {!isTalent && !isMentor && !isOrgAdmin && !isSchoolAdmin && (
        <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>
          Pick a role from Settings to unlock your home.
        </p>
      )}
    </div>
  );
}


// ─── Shared header ──────────────────────────────────────────────────────────
function Header({ user }) {
  const navigate = useNavigate();
  return (
    <div className="flex justify-between items-center mb-6">
      <div className="flex items-center gap-3">
        <Avatar name={user?.full_name || 'User'} size={44} />
        <div>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Welcome back</p>
          <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
            {user?.full_name || 'User'}
          </p>
        </div>
      </div>
      <button onClick={() => navigate('/app/notifications')}
              className="w-10 h-10 rounded-full border flex items-center justify-center hover:bg-gray-50"
              style={{ borderColor: 'var(--border)' }}>
        <Bell size={18} />
      </button>
    </div>
  );
}


// ─── Talent home (existing content) ─────────────────────────────────────────
function adaptJob(op) {
  return {
    id: op.id,
    title: op.title,
    company: op.organization?.name || 'SkillBridge',
    companyKey: (op.organization?.name || '').toLowerCase().replace(/\s/g, ''),
    location: op.location || (op.is_remote ? 'Remote' : 'On-site'),
    type: op.opportunity_type === 'internship' ? 'Internship'
         : op.opportunity_type === 'micro_project' ? 'Micro-Project'
         : op.opportunity_type === 'guided_project' ? 'Guided Project'
         : 'Opportunity',
    mode: op.is_remote ? 'Remote' : 'Onsite',
    salaryMin: 0, salaryMax: 0,
    compensationLabel: op.compensation || (op.is_paid ? 'Paid' : 'Unpaid'),
    deadline: op.application_deadline
      ? new Date(op.application_deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
      : 'Open',
    daysLeft: op.application_deadline
      ? Math.max(0, Math.ceil((new Date(op.application_deadline) - Date.now()) / 86400000))
      : null,
    applicants: op.applicant_count ?? 0,
    category: op.required_skills?.[0]?.category || 'Others',
    saved: false,
    description: op.description,
    responsibilities: [],
    requirements: (op.required_skills || []).map(s => s.name),
    aboutCompany: op.organization?.description || '',
  };
}

function TalentHome() {
  const navigate = useNavigate();
  const { data: rawJobs, loading, error } = useApi(getOpportunities);
  const jobs = (rawJobs || []).map(adaptJob);
  const recentJobs = jobs.slice(0, 4);
  const recommendedJobs = jobs.slice(0, 6);

  const categories = useMemo(() => {
    const set = new Set(jobs.map(j => j.category).filter(Boolean));
    return Array.from(set).map(label => ({ id: label, label }));
  }, [jobs]);
  const [activeCategory, setActiveCategory] = useState(null);

  return (
    <>
      <h1 className="text-2xl font-bold mb-5" style={{ color: 'var(--text-primary)' }}>
        Explore Top Opportunities
      </h1>

      <div className="flex gap-2 mb-8">
        <div className="flex-1 relative">
          <input placeholder="Search opportunities..."
                 onFocus={() => navigate('/app/search')} readOnly
                 className="w-full pl-4 pr-4 py-3 rounded-full text-sm border"
                 style={{ background: 'white', borderColor: 'var(--border)' }} />
        </div>
        <button onClick={() => navigate('/app/jobs')}
                className="w-12 h-12 rounded-full flex items-center justify-center border"
                style={{ background: 'white', borderColor: 'var(--border)' }}>
          <SlidersHorizontal size={18} style={{ color: 'var(--text-secondary)' }} />
        </button>
      </div>

      {categories.length > 0 && (
        <div className="mb-8">
          <SectionHeader title="Categories" onSeeAll={() => navigate('/app/jobs')} />
          <div className="flex flex-wrap gap-2">
            {categories.map(cat => (
              <button key={cat.id} onClick={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
                className="px-4 py-2 rounded-full text-sm border transition-all"
                style={{
                  background: activeCategory === cat.id ? 'var(--text-primary)' : 'white',
                  color: activeCategory === cat.id ? '#fff' : 'var(--text-primary)',
                  borderColor: activeCategory === cat.id ? 'var(--text-primary)' : 'var(--border)',
                }}>
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && <p className="text-sm py-8 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm py-8 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && (
        <>
          <div className="mb-8">
            <SectionHeader title="Recent Opportunities" onSeeAll={() => navigate('/app/jobs')} />
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {recentJobs.map(job => <JobCardSmall key={job.id} job={job} />)}
            </div>
          </div>
          <div>
            <SectionHeader title="Recommended" onSeeAll={() => navigate('/app/jobs')} />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendedJobs.map(job => <JobCardWide key={job.id} job={job} />)}
            </div>
          </div>
        </>
      )}
    </>
  );
}


// ─── Mentor home ────────────────────────────────────────────────────────────
function MentorHome() {
  const navigate = useNavigate();
  const { data: mentorships } = useApi(() => listMyMentorships('active'));
  const { data: profile } = useApi(getMyMentorProfile);
  const activeCount = (mentorships || []).length;

  return (
    <>
      <div className="flex items-start justify-between mb-5 gap-3 flex-wrap">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Mentor Dashboard
        </h1>
        <button onClick={() => navigate('/app/mentor/post-project')}
                className="flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium text-white"
                style={{ background: 'var(--text-primary)' }}>
          <Plus size={14} /> Post guided project
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Active mentees" value={activeCount} />
        <StatCard label="Max mentees" value={profile?.max_mentees ?? '—'} />
        <StatCard label="Endorsements given" value={profile?.endorsements_given ?? 0} />
      </div>

      {/* Top talents to discover */}
      <TopTalentsSection
        title="Explore Top Talents"
        seeAllPath="/app/talent"
        emptyMsg="No talents to show yet." />

      {/* My active mentorships */}
      <div className="mt-8">
        <SectionHeader title="My Active Mentees"
                       onSeeAll={() => navigate('/app/mentor/mentorships')} />
        {(mentorships || []).length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            You don't have active mentees yet. Add one from "My Mentorships".
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {(mentorships || []).slice(0, 3).map(m => (
              <div key={m.id}
                   onClick={() => navigate(`/app/mentor/mentorships/${m.id}`)}
                   className="bg-white rounded-2xl p-4 border cursor-pointer hover:shadow-md"
                   style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-3">
                  <Avatar name={m.talent?.full_name || m.talent?.email} size={36} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                      {m.talent?.full_name || m.talent?.email}
                    </p>
                    <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                      {m.focus_area || m.talent?.headline || '—'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}


// ─── Org home ───────────────────────────────────────────────────────────────
function OrgHome() {
  const navigate = useNavigate();
  const { data: org, error: orgError } = useApi(getMyOrganization);

  // If org admin hasn't created their org yet, push them to setup.
  if (orgError && /no_organization|not a member/i.test(orgError)) {
    return (
      <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: 'var(--border)' }}>
        <p className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          Set up your organization
        </p>
        <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
          You haven't created an organization yet. Set one up to start posting opportunities.
        </p>
        <button onClick={() => navigate('/create-organization')}
                className="rounded-full px-4 py-2 text-sm font-medium text-white"
                style={{ background: 'var(--text-primary)' }}>
          Create organization
        </button>
      </div>
    );
  }

  return (
    <>
      <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
        {org?.name || 'Organization Dashboard'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
        Find talent and manage opportunities.
      </p>

      {/* Quick actions */}
      <div className="flex flex-wrap gap-3 mb-8">
        <button onClick={() => navigate('/app/org/opportunities')}
                className="flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium text-white"
                style={{ background: 'var(--text-primary)' }}>
          <Plus size={14} /> New opportunity
        </button>
        <button onClick={() => navigate('/app/org/profile')}
                className="rounded-full px-4 py-2 text-sm font-medium border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
          Organization profile
        </button>
      </div>

      {/* AI Proactive Sourcing */}
      <ProactiveSourcingPreview orgId={org?.id} />

      {/* Top talents */}
      <div className="mt-8">
        <TopTalentsSection
          title="Explore Top Talents"
          seeAllPath="/app/talent"
          emptyMsg="No talents to show yet." />
      </div>
    </>
  );
}


function ProactiveSourcingPreview({ orgId }) {
  const navigate = useNavigate();
  const { data, loading, aiDisabled, refresh } = useAIInsight(
    () => orgId ? getProactiveSourcing(orgId) : Promise.resolve(null),
    [orgId],
  );
  if (aiDisabled) return null;
  const matches = data?.matches || [];

  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} style={{ color: 'var(--text-secondary)' }} />
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            AI Proactive Sourcing
          </p>
          {data?.confidence && (
            <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                  style={{
                    background: data.confidence === 'medium' ? '#DBEAFE' : '#FEF3C7',
                    color:      data.confidence === 'medium' ? '#1E40AF' : '#92400E',
                  }}>
              {data.confidence}
            </span>
          )}
        </div>
        <button onClick={refresh} title="Refresh">
          <RefreshCw size={14} style={{ color: 'var(--text-muted)' }} />
        </button>
      </div>
      {data?.confidence_reason && (
        <p className="text-xs mb-3 italic" style={{ color: 'var(--text-muted)' }}>{data.confidence_reason}</p>
      )}
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Finding candidates…</p>}
      {!loading && matches.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          No suggestions yet. Hire a few applicants and AI will surface similar talents here.
        </p>
      )}
      <div className="flex flex-col gap-2">
        {matches.slice(0, 3).map(m => (
          <div key={m.talent_id}
               onClick={() => navigate(`/app/talent/${m.talent_id}`)}
               className="flex items-center gap-3 p-2 rounded-lg border cursor-pointer hover:bg-gray-50"
               style={{ borderColor: 'var(--border)' }}>
            <Avatar name={m.talent?.full_name} size={36} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                {m.talent?.full_name} <span className="text-xs" style={{ color: 'var(--text-muted)' }}>· fit {m.fit_score}</span>
              </p>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{m.reason}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ─── School home (redirect-ish) ─────────────────────────────────────────────
function SchoolHome() {
  const navigate = useNavigate();
  return (
    <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: 'var(--border)' }}>
      <p className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>School Dashboard</p>
      <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
        Verify students and see how your curriculum aligns with market demand.
      </p>
      <button onClick={() => navigate('/app/school')}
              className="rounded-full px-4 py-2 text-sm font-medium text-white"
              style={{ background: 'var(--text-primary)' }}>
        Open School Dashboard
      </button>
    </div>
  );
}


// ─── Shared: Top Talents section (used by Mentor + Org homes) ───────────────
function TopTalentsSection({ title, seeAllPath, emptyMsg }) {
  const navigate = useNavigate();
  const { data: talents, loading, error } = useApi(
    () => listTalents({ is_available: true, limit: 6, ordering: '-updated_at' }),
  );

  return (
    <div>
      <SectionHeader title={title} onSeeAll={() => navigate(seeAllPath)} />
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading talents…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {!loading && !error && (talents || []).length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{emptyMsg}</p>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {(talents || []).map(t => {
          const name = t.user?.full_name || t.user?.email || '—';
          return (
            <div key={t.id}
                 onClick={() => navigate(`/app/talent/${t.id}`)}
                 className="bg-white rounded-2xl p-4 border cursor-pointer hover:shadow-md transition-shadow"
                 style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-start gap-3 mb-2">
                <Avatar name={name} size={40} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                    {name}
                  </p>
                  <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                    {t.headline || '—'}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1">
                {(t.skills || []).slice(0, 3).map(s => (
                  <span key={s.skill?.id || s.id}
                        className="text-xs px-2 py-0.5 rounded-full font-medium text-white"
                        style={{ background: 'var(--text-primary)' }}>
                    {s.skill?.name || s.name}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-2xl p-4 border" style={{ borderColor: 'var(--border)' }}>
      <p className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>{value}</p>
    </div>
  );
}
