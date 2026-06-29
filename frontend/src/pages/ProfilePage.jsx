import { useRef, useState, useEffect, useMemo } from 'react';
import { Pencil, Plus, X, RefreshCw, ShieldCheck, Sparkles, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { updateMe } from '../api/auth';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import {
  getMyTalentProfile, updateMyTalentProfile,
  addSkill, removeSkill,
} from '../api/talents';
import { getSkills, createSkill } from '../api/core';
import {
  getMyTrustScore, getMySkillRoadmap, getMentorMatches,
} from '../api/ai';
import { uploadToSupabase } from '../api/uploads';
import { Button, PageHeader } from '../components/UI';

const EDUCATION_ROUTES = [
  { value: 'university',  label: 'University' },
  { value: 'polytechnic', label: 'Polytechnic' },
  { value: 'bootcamp',    label: 'Bootcamp' },
  { value: 'self_taught', label: 'Self-Taught' },
];

const PROFICIENCY = ['beginner', 'intermediate', 'advanced', 'expert'];


// ── Trust Score card ────────────────────────────────────────────────────────
function TrustScoreCard() {
  const { data, loading, error, aiDisabled, refresh } = useAIInsight(
    ({ refresh, signal } = {}) => getMyTrustScore({ refresh }),
  );
  if (aiDisabled) return null;
  const score = data?.payload?.score;
  return (
    <Card title="Trust Score" icon={ShieldCheck} onRefresh={refresh}>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Computing…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {data && (
        <>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-4xl font-bold" style={{ color: 'var(--text-primary)' }}>{score}</span>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>/ 100</span>
          </div>
          {data.payload.rationale && (
            <p className="text-xs mb-3" style={{ color: 'var(--text-secondary)' }}>
              {data.payload.rationale}
            </p>
          )}
          <div className="flex flex-col gap-1">
            {Object.entries(data.payload.components || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs">
                <span style={{ color: 'var(--text-muted)' }} className="capitalize">
                  {k.replace(/_/g, ' ')}
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  {v} / {data.payload.weights?.[k] ?? '—'}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </Card>
  );
}


// ── Skill Roadmap card ──────────────────────────────────────────────────────
function SkillRoadmapCard() {
  const { data, loading, error, aiDisabled, refresh } = useAIInsight(
    ({ refresh } = {}) => getMySkillRoadmap({ refresh }),
  );
  if (aiDisabled) return null;
  return (
    <Card title="Skill Roadmap" icon={Sparkles} onRefresh={refresh}>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Generating…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {data?.payload && (
        <>
          {data.payload.summary && (
            <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>{data.payload.summary}</p>
          )}
          <ol className="flex flex-col gap-2 list-decimal pl-4">
            {(data.payload.steps || []).slice(0, 5).map((step, i) => (
              <li key={i} className="text-sm" style={{ color: 'var(--text-primary)' }}>
                <span className="font-medium">{step.title || step.skill}</span>
                {step.rationale && (
                  <span className="block text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {step.rationale}
                  </span>
                )}
              </li>
            ))}
          </ol>
          {(data.payload.steps || []).length === 0 && (
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              No gaps detected yet. Apply to a few opportunities so we can learn what to recommend.
            </p>
          )}
        </>
      )}
    </Card>
  );
}


// ── Mentor Matches card ─────────────────────────────────────────────────────
function MentorMatchesCard() {
  const { data, loading, error, aiDisabled } = useAIInsight(
    () => getMentorMatches(),
  );
  if (aiDisabled) return null;
  const matches = data?.matches || [];
  return (
    <Card title="Suggested Mentors" icon={Users}>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Finding mentors…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {!loading && matches.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          No mentor matches yet. Add more skills to improve recommendations.
        </p>
      )}
      <div className="flex flex-col gap-2">
        {matches.slice(0, 3).map(m => (
          <div key={m.mentor_id} className="p-3 rounded-xl border" style={{ borderColor: 'var(--border)' }}>
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {m.mentor?.full_name}
            </p>
            {m.mentor?.headline && (
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{m.mentor.headline}</p>
            )}
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{m.reason}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}


// ── Card primitive ──────────────────────────────────────────────────────────
function Card({ title, icon: Icon, onRefresh, children }) {
  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {Icon && <Icon size={16} style={{ color: 'var(--text-secondary)' }} />}
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</p>
        </div>
        {onRefresh && (
          <button onClick={onRefresh} title="Recompute"
                  className="p-1 rounded hover:bg-gray-100">
            <RefreshCw size={14} style={{ color: 'var(--text-muted)' }} />
          </button>
        )}
      </div>
      {children}
    </div>
  );
}


// ── Skills editor ───────────────────────────────────────────────────────────
function SkillsSection({ profile, onChange }) {
  const { data: allSkills, refetch: refetchSkills } = useApi(getSkills);
  const [adding, setAdding] = useState(false);
  const [selectedSkillId, setSelectedSkillId] = useState('');
  const [customName, setCustomName] = useState('');
  const [proficiency, setProficiency] = useState('intermediate');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const ownedIds = useMemo(
    () => new Set((profile?.skills || []).map(s => s.skill?.id)),
    [profile]
  );
  const pickable = (allSkills || []).filter(s => !ownedIds.has(s.id));

  const handleAdd = async () => {
    // Resolve a skill_id: either an existing canonical pick, or find-or-create
    // from the typed name. This lets users add skills the platform doesn't
    // know about yet (e.g. niche frameworks).
    let skillId = selectedSkillId ? parseInt(selectedSkillId, 10) : null;
    setBusy(true); setError('');
    try {
      if (!skillId && customName.trim()) {
        const created = await createSkill(customName.trim());
        skillId = created.id;
        await refetchSkills();
      }
      if (!skillId) {
        setError('Pick a skill or type a new one.');
        setBusy(false);
        return;
      }
      await addSkill({
        skill_id: skillId,
        proficiency,
        years_experience: 0,
        is_primary: false,
      });
      setSelectedSkillId(''); setCustomName(''); setAdding(false);
      await onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const handleRemove = async (skillId) => {
    setBusy(true); setError('');
    try {
      await removeSkill(skillId);
      await onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Skills</p>
        {!adding && (
          <button onClick={() => setAdding(true)} className="flex items-center gap-1 text-xs font-medium"
                  style={{ color: 'var(--text-primary)' }}>
            <Plus size={14} /> Add
          </button>
        )}
      </div>

      {error && <p className="text-xs mb-2" style={{ color: 'var(--red)' }}>{error}</p>}

      <div className="flex flex-wrap gap-2 mb-3">
        {(profile?.skills || []).map(s => (
          <span key={s.skill?.id || s.id}
                className="text-xs px-2.5 py-1 rounded-full font-medium border flex items-center gap-1"
                style={{
                  background: s.is_endorsed ? '#D1FAE5' : 'transparent',
                  color: s.is_endorsed ? '#065F46' : 'var(--text-primary)',
                  borderColor: 'var(--border)',
                }}>
            {s.skill?.name}
            <span className="text-xs opacity-60">· {s.proficiency}</span>
            {s.is_endorsed && <span title="Endorsed by mentor">✓</span>}
            <button onClick={() => handleRemove(s.skill.id)} disabled={busy} className="ml-1 hover:opacity-60">
              <X size={12} />
            </button>
          </span>
        ))}
        {(profile?.skills || []).length === 0 && (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No skills yet.</p>
        )}
      </div>

      {adding && (
        <div className="flex flex-col gap-2 mt-3 p-3 rounded-xl border" style={{ borderColor: 'var(--border)' }}>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Pick from the list <em>or</em> type a new skill below — we'll add it.
          </p>
          <select value={selectedSkillId}
                  onChange={e => { setSelectedSkillId(e.target.value); if (e.target.value) setCustomName(''); }}
                  className="text-sm px-3 py-2 rounded-lg border" style={{ borderColor: 'var(--border)' }}>
            <option value="">Choose an existing skill…</option>
            {pickable.map(s => (
              <option key={s.id} value={s.id}>{s.name} {s.category && `· ${s.category}`}</option>
            ))}
          </select>
          <input value={customName}
                 onChange={e => { setCustomName(e.target.value); if (e.target.value) setSelectedSkillId(''); }}
                 placeholder="Or type a new skill (e.g., Rust, LangChain)"
                 className="text-sm px-3 py-2 rounded-lg border" style={{ borderColor: 'var(--border)' }} />
          <select value={proficiency} onChange={e => setProficiency(e.target.value)}
                  className="text-sm px-3 py-2 rounded-lg border capitalize" style={{ borderColor: 'var(--border)' }}>
            {PROFICIENCY.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <div className="flex gap-2">
            <button onClick={handleAdd} disabled={busy || (!selectedSkillId && !customName.trim())}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium text-white disabled:opacity-50"
                    style={{ background: 'var(--text-primary)' }}>
              {busy ? 'Adding…' : 'Add skill'}
            </button>
            <button onClick={() => { setAdding(false); setSelectedSkillId(''); setCustomName(''); setError(''); }}
                    className="px-3 py-1.5 text-xs">
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


// ── ProfilePage main ────────────────────────────────────────────────────────
export default function ProfilePage() {
  const { user, refreshUser, isTalent } = useAuth();

  // Talent profile (only if user is a talent)
  const {
    data: talentProfile, loading: profileLoading, error: profileError, refetch: refetchProfile,
  } = useApi(() => isTalent ? getMyTalentProfile() : Promise.resolve(null), [isTalent]);

  const [fullName, setFullName] = useState('');
  const [phone, setPhone]       = useState('');
  const [headline, setHeadline] = useState('');
  const [bio, setBio]           = useState('');
  const [educationRoute, setEducationRoute] = useState('self_taught');
  const [institutionName,  setInstitutionName]  = useState('');
  const [fieldOfStudy,     setFieldOfStudy]     = useState('');
  const [graduationYear,   setGraduationYear]   = useState('');
  const [city,        setCity]       = useState('');
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [githubUrl,    setGithubUrl]    = useState('');
  const [linkedinUrl,  setLinkedinUrl]  = useState('');
  const [isAvailable,  setIsAvailable]  = useState(true);

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [avatarError, setAvatarError] = useState('');
  const avatarFileRef = useRef(null);

  const handleAvatarPick = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarUploading(true); setAvatarError('');
    try {
      const url = await uploadToSupabase(file, 'avatar');
      await updateMe({ avatar_url: url });
      await refreshUser();
    } catch (err) {
      setAvatarError(err.message);
    } finally {
      setAvatarUploading(false);
      if (avatarFileRef.current) avatarFileRef.current.value = '';
    }
  };

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setPhone(user.phone_number || '');
    }
  }, [user]);

  useEffect(() => {
    if (talentProfile) {
      setHeadline(talentProfile.headline || '');
      setBio(talentProfile.bio || '');
      setEducationRoute(talentProfile.education_route || 'self_taught');
      setInstitutionName(talentProfile.institution_name || '');
      setFieldOfStudy(talentProfile.field_of_study || '');
      setGraduationYear(talentProfile.graduation_year || '');
      setCity(talentProfile.city || '');
      setPortfolioUrl(talentProfile.portfolio_url || '');
      setGithubUrl(talentProfile.github_url || '');
      setLinkedinUrl(talentProfile.linkedin_url || '');
      setIsAvailable(talentProfile.is_available ?? true);
    }
  }, [talentProfile]);

  const handleSave = async () => {
    setSaving(true); setError(''); setSuccess(false);
    try {
      await updateMe({ full_name: fullName, phone_number: phone });
      if (isTalent) {
        await updateMyTalentProfile({
          headline, bio,
          education_route: educationRoute,
          institution_name: institutionName,
          field_of_study: fieldOfStudy,
          graduation_year: graduationYear ? parseInt(graduationYear, 10) : null,
          city,
          portfolio_url: portfolioUrl,
          github_url: githubUrl,
          linkedin_url: linkedinUrl,
          is_available: isAvailable,
        });
      }
      await refreshUser();
      await refetchProfile();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?';

  return (
    <div className="p-8 max-w-3xl">
      <PageHeader title="My Profile" onBack />

      {/* Avatar */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative mb-3">
          {user?.avatar_url ? (
            <img src={user.avatar_url} alt={user.full_name || 'avatar'}
                 className="w-20 h-20 rounded-full object-cover"
                 style={{ background: '#D1D5DB' }} />
          ) : (
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-semibold"
                 style={{ background: '#D1D5DB', color: '#374151' }}>
              {initials}
            </div>
          )}
          <input ref={avatarFileRef} type="file" accept="image/png,image/jpeg,image/webp"
                 className="hidden" onChange={handleAvatarPick} />
          <button onClick={() => avatarFileRef.current?.click()} disabled={avatarUploading}
                  title={avatarUploading ? 'Uploading…' : 'Change photo'}
                  className="absolute bottom-0 right-0 w-7 h-7 rounded-full flex items-center justify-center shadow-sm disabled:opacity-50"
                  style={{ background: 'var(--text-primary)' }}>
            <Pencil size={13} color="white" />
          </button>
        </div>
        {avatarError && (
          <p className="text-xs mb-1" style={{ color: 'var(--red)' }}>{avatarError}</p>
        )}
        <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{user?.full_name || '—'}</p>
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user?.email}</p>
      </div>

      {/* AI Insights row (talents only) */}
      {isTalent && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <TrustScoreCard />
          <SkillRoadmapCard />
          <MentorMatchesCard />
        </div>
      )}

      {/* User fields (all users) */}
      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Account</p>
        <Field label="Name" value={fullName} onChange={setFullName} />
        <Field label="Email" value={user?.email || ''} disabled />
        <Field label="Phone Number" value={phone} onChange={setPhone} type="tel" />
      </div>

      {/* TalentProfile fields */}
      {isTalent && profileLoading && (
        <p className="text-sm py-4" style={{ color: 'var(--text-muted)' }}>Loading profile…</p>
      )}
      {isTalent && profileError && (
        <p className="text-sm py-4" style={{ color: 'var(--red)' }}>{profileError}</p>
      )}
      {isTalent && talentProfile && (
        <>
          <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
            <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Professional</p>
            <Field label="Headline" value={headline} onChange={setHeadline}
                   placeholder="e.g. Full-stack developer · React + Django" />
            <Field label="Bio" value={bio} onChange={setBio} multiline />
            <div className="mt-2 flex items-center gap-2">
              <input type="checkbox" id="avail" checked={isAvailable} onChange={e => setIsAvailable(e.target.checked)} />
              <label htmlFor="avail" className="text-sm" style={{ color: 'var(--text-primary)' }}>
                Open to new opportunities
              </label>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
            <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Education</p>
            <div className="mb-3">
              <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>Education route</p>
              <select value={educationRoute} onChange={e => setEducationRoute(e.target.value)}
                      className="w-full px-3 py-2 text-sm border rounded-lg"
                      style={{ borderColor: 'var(--border)' }}>
                {EDUCATION_ROUTES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <Field label="Institution" value={institutionName} onChange={setInstitutionName} />
            <Field label="Field of study" value={fieldOfStudy} onChange={setFieldOfStudy} />
            <Field label="Graduation year" value={graduationYear} onChange={setGraduationYear} type="number" />
            <Field label="City" value={city} onChange={setCity} />
          </div>

          <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
            <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Links</p>
            <Field label="Portfolio URL" value={portfolioUrl} onChange={setPortfolioUrl} type="url" />
            <Field label="GitHub URL"    value={githubUrl}    onChange={setGithubUrl}    type="url" />
            <Field label="LinkedIn URL"  value={linkedinUrl}  onChange={setLinkedinUrl}  type="url" />
          </div>

          <div className="mb-4">
            <SkillsSection profile={talentProfile} onChange={refetchProfile} />
          </div>
        </>
      )}

      {error && <p className="text-sm mt-4" style={{ color: 'var(--red)' }}>{error}</p>}
      {success && <p className="text-sm mt-4" style={{ color: 'var(--green)' }}>Profile updated.</p>}

      <div className="mt-6">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving…' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}


// ── Field primitive ─────────────────────────────────────────────────────────
function Field({ label, value, onChange, type = 'text', placeholder, disabled, multiline }) {
  return (
    <div className="mb-3">
      <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      {multiline ? (
        <textarea value={value || ''} onChange={e => onChange?.(e.target.value)} disabled={disabled}
                  rows={3} placeholder={placeholder}
                  className="w-full px-3 py-2 text-sm border rounded-lg resize-y"
                  style={{ borderColor: 'var(--border)',
                           color: disabled ? 'var(--text-muted)' : 'var(--text-primary)',
                           background: disabled ? '#F9F9F7' : 'white' }} />
      ) : (
        <input type={type} value={value || ''} onChange={e => onChange?.(e.target.value)} disabled={disabled}
               placeholder={placeholder}
               className="w-full px-0 py-2 text-sm border-b bg-transparent"
               style={{ borderColor: 'var(--border)',
                        color: disabled ? 'var(--text-muted)' : 'var(--text-primary)',
                        cursor: disabled ? 'not-allowed' : 'text' }} />
      )}
    </div>
  );
}
