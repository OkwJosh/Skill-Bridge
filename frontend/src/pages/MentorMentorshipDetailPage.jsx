import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calendar, Activity, Sparkles, RefreshCw, Trash2 } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import {
  getMyMentorship, updateMentorship,
  listSessions, createSession, updateSession, deleteSession,
  listMentorActivities, createEndorsement,
} from '../api/mentors';
import { getTalentProfile } from '../api/talents';
import { getMenteeProgressInsight } from '../api/ai';
import { Avatar, Button, PageHeader } from '../components/UI';


const SESSION_STATUSES = ['scheduled', 'completed', 'cancelled', 'no_show'];

export default function MentorMentorshipDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: m, loading, error, refetch: refetchM } = useApi(() => getMyMentorship(id), [id]);
  const talentId = m?.talent?.id;
  const { data: talentProfile, refetch: refetchTalent } = useApi(
    () => talentId ? getTalentProfile(talentId) : Promise.resolve(null),
    [talentId],
  );

  if (loading) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Loading…</p></div>;
  if (error)   return <div className="p-8"><p style={{ color: 'var(--red)' }}>{error}</p></div>;
  if (!m)      return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Not found.</p></div>;

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader title="Mentorship" onBack />

      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border mb-6 flex items-start gap-4" style={{ borderColor: 'var(--border)' }}>
        <Avatar name={m.talent?.full_name || m.talent?.email} size={56} />
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
            {m.talent?.full_name || m.talent?.email}
          </p>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{m.talent?.headline || '—'}</p>
          {m.focus_area && (
            <p className="text-xs italic mt-2" style={{ color: 'var(--text-secondary)' }}>
              Focus: "{m.focus_area}"
            </p>
          )}
        </div>
        <StatusControl mentorship={m} onChange={refetchM} />
      </div>

      {/* AI Progress Insight */}
      <ProgressInsightCard mentorshipId={m.id} />

      {/* Sessions */}
      <SessionsSection mentorshipId={m.id} />

      {/* Activities */}
      <ActivitiesSection mentorshipId={m.id} />

      {/* Endorse skill */}
      {talentProfile && (
        <EndorseSection talent={talentProfile} onEndorsed={refetchTalent} />
      )}
    </div>
  );
}


// ── Status control ─────────────────────────────────────────────────────────
function StatusControl({ mentorship, onChange }) {
  const [busy, setBusy] = useState(false);
  const setStatus = async (newStatus) => {
    if (newStatus === mentorship.status) return;
    setBusy(true);
    try {
      await updateMentorship(mentorship.id, { status: newStatus });
      await onChange();
    } finally {
      setBusy(false);
    }
  };
  return (
    <select value={mentorship.status}
            onChange={e => setStatus(e.target.value)}
            disabled={busy}
            className="text-xs px-2 py-1 rounded border capitalize"
            style={{ borderColor: 'var(--border)' }}>
      {['active', 'paused', 'ended'].map(s => <option key={s} value={s}>{s}</option>)}
    </select>
  );
}


// ── AI Progress Insight ────────────────────────────────────────────────────
function ProgressInsightCard({ mentorshipId }) {
  const { data, loading, error, aiDisabled, refresh } = useAIInsight(
    () => getMenteeProgressInsight(mentorshipId),
    [mentorshipId],
  );
  if (aiDisabled) return null;
  const payload = data?.payload;

  return (
    <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} style={{ color: 'var(--text-secondary)' }} />
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Pre-session Brief (AI)
          </p>
        </div>
        <button onClick={refresh} title="Refresh">
          <RefreshCw size={14} style={{ color: 'var(--text-muted)' }} />
        </button>
      </div>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Generating…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {payload && (
        <>
          <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>{payload.summary}</p>
          {payload.note_if_no_activity && (
            <p className="text-xs italic mb-3" style={{ color: 'var(--text-muted)' }}>
              {payload.note_if_no_activity}
            </p>
          )}
          {(payload.wins?.length > 0 || payload.blockers?.length > 0) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InsightCol title="Wins" color="#065F46" items={payload.wins} />
              <InsightCol title="Blockers" color="#991B1B" items={payload.blockers} />
              <InsightCol title="Suggested topics" color="var(--text-primary)" items={payload.suggested_topics} />
            </div>
          )}
        </>
      )}
    </div>
  );
}

function InsightCol({ title, color, items }) {
  if (!items?.length) return null;
  return (
    <div>
      <p className="text-xs font-semibold mb-2 uppercase tracking-wide" style={{ color }}>{title}</p>
      <ul className="text-sm space-y-1 list-disc pl-5" style={{ color: 'var(--text-secondary)' }}>
        {items.map((it, i) => <li key={i}>{it}</li>)}
      </ul>
    </div>
  );
}


// ── Sessions ───────────────────────────────────────────────────────────────
function SessionsSection({ mentorshipId }) {
  const { data: sessions, loading, refetch } = useApi(
    () => listSessions(mentorshipId), [mentorshipId],
  );
  const [adding, setAdding] = useState(false);
  const [scheduledFor, setScheduledFor] = useState('');
  const [duration, setDuration] = useState(30);
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const handleCreate = async () => {
    if (!scheduledFor) { setError('Date/time required.'); return; }
    setBusy(true); setError('');
    try {
      await createSession(mentorshipId, {
        scheduled_for: new Date(scheduledFor).toISOString(),
        duration_minutes: parseInt(duration, 10),
        topic, status: 'scheduled',
      });
      setScheduledFor(''); setTopic(''); setAdding(false);
      await refetch();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Calendar size={16} style={{ color: 'var(--text-secondary)' }} />
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Sessions</p>
        </div>
        <button onClick={() => setAdding(o => !o)} className="text-xs font-medium underline"
                style={{ color: 'var(--text-primary)' }}>
          {adding ? 'Cancel' : '+ Schedule'}
        </button>
      </div>

      {adding && (
        <div className="bg-gray-50 p-3 rounded-xl mb-3 flex flex-col gap-2">
          <input type="datetime-local" value={scheduledFor}
                 onChange={e => setScheduledFor(e.target.value)}
                 className="px-3 py-2 text-sm rounded border" style={{ borderColor: 'var(--border)' }} />
          <input type="number" value={duration} onChange={e => setDuration(e.target.value)}
                 placeholder="Duration (minutes)"
                 className="px-3 py-2 text-sm rounded border" style={{ borderColor: 'var(--border)' }} />
          <input value={topic} onChange={e => setTopic(e.target.value)}
                 placeholder="Topic (optional)"
                 className="px-3 py-2 text-sm rounded border" style={{ borderColor: 'var(--border)' }} />
          {error && <p className="text-xs" style={{ color: 'var(--red)' }}>{error}</p>}
          <Button onClick={handleCreate} disabled={busy}>{busy ? 'Saving…' : 'Schedule session'}</Button>
        </div>
      )}

      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {!loading && (sessions || []).length === 0 && !adding && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No sessions yet.</p>
      )}

      <div className="flex flex-col gap-2">
        {(sessions || []).map(s => <SessionRow key={s.id} session={s} onChange={refetch} />)}
      </div>
    </div>
  );
}

function SessionRow({ session, onChange }) {
  const [editing, setEditing] = useState(false);
  const [notes, setNotes] = useState(session.private_notes || '');
  const [status, setStatus] = useState(session.status);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    setBusy(true);
    try {
      await updateSession(session.id, { private_notes: notes, status });
      setEditing(false);
      await onChange();
    } finally { setBusy(false); }
  };

  const remove = async () => {
    if (!confirm('Delete this session?')) return;
    setBusy(true);
    try {
      await deleteSession(session.id);
      await onChange();
    } finally { setBusy(false); }
  };

  return (
    <div className="border rounded-lg p-3" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between gap-3 mb-1">
        <div className="text-sm" style={{ color: 'var(--text-primary)' }}>
          {new Date(session.scheduled_for).toLocaleString()} · {session.duration_minutes}m
        </div>
        <div className="flex items-center gap-2">
          {editing ? (
            <select value={status} onChange={e => setStatus(e.target.value)}
                    className="text-xs px-2 py-1 rounded border capitalize" style={{ borderColor: 'var(--border)' }}>
              {SESSION_STATUSES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
          ) : (
            <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                  style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
              {session.status.replace('_', ' ')}
            </span>
          )}
          <button onClick={() => setEditing(e => !e)} className="text-xs underline"
                  style={{ color: 'var(--text-primary)' }}>{editing ? 'Cancel' : 'Edit'}</button>
          <button onClick={remove} className="text-xs"><Trash2 size={12} style={{ color: 'var(--red)' }} /></button>
        </div>
      </div>
      {session.topic && (
        <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>{session.topic}</p>
      )}
      {editing ? (
        <>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3}
                    placeholder="Private notes (only you see these)"
                    className="w-full text-sm px-2 py-1 border rounded" style={{ borderColor: 'var(--border)' }} />
          <Button onClick={save} disabled={busy} className="mt-2">{busy ? 'Saving…' : 'Save'}</Button>
        </>
      ) : session.private_notes ? (
        <p className="text-xs italic" style={{ color: 'var(--text-muted)' }}>{session.private_notes}</p>
      ) : null}
    </div>
  );
}


// ── Activities ─────────────────────────────────────────────────────────────
function ActivitiesSection({ mentorshipId }) {
  const { data, loading } = useApi(() => listMentorActivities(mentorshipId), [mentorshipId]);
  const items = data || [];
  return (
    <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-3">
        <Activity size={16} style={{ color: 'var(--text-secondary)' }} />
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Recent Activity</p>
      </div>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {!loading && items.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Mentee hasn't logged any activity.</p>
      )}
      <div className="flex flex-col gap-2">
        {items.slice(0, 10).map(a => (
          <div key={a.id} className="flex items-start gap-2 text-sm">
            <span className="text-xs px-2 py-0.5 rounded-full capitalize whitespace-nowrap"
                  style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
              {a.activity_type.replace(/_/g, ' ')}
            </span>
            <div className="flex-1">
              <p style={{ color: 'var(--text-primary)' }}>{a.description}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {new Date(a.occurred_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ── Endorse a skill ─────────────────────────────────────────────────────────
function EndorseSection({ talent, onEndorsed }) {
  const unendorsed = (talent.skills || []).filter(s => !s.is_endorsed);
  const [selectedSkillId, setSelectedSkillId] = useState('');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handle = async () => {
    if (!selectedSkillId) { setError('Pick a skill to endorse.'); return; }
    setBusy(true); setError(''); setSuccess('');
    try {
      await createEndorsement({
        talent_profile_id: talent.id,
        skill_id: parseInt(selectedSkillId, 10),
        endorsement_note: note,
      });
      setSuccess('Endorsement recorded.');
      setSelectedSkillId(''); setNote('');
      await onEndorsed();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <p className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
        Endorse a skill
      </p>
      <p className="text-xs mb-3" style={{ color: 'var(--text-muted)' }}>
        A verified endorsement raises this mentee's Trust Score (endorsements
        are worth up to 40 of 100 points) and is visible to employers.
      </p>
      {unendorsed.length === 0 ? (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          All of this talent's skills are already endorsed.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          <select value={selectedSkillId} onChange={e => setSelectedSkillId(e.target.value)}
                  className="text-sm px-3 py-2 rounded-lg border" style={{ borderColor: 'var(--border)' }}>
            <option value="">Choose a skill…</option>
            {unendorsed.map(s => (
              <option key={s.skill?.id} value={s.skill?.id}>
                {s.skill?.name} ({s.proficiency})
              </option>
            ))}
          </select>
          <textarea value={note} onChange={e => setNote(e.target.value)} rows={2}
                    placeholder="Endorsement note (visible to employers)"
                    className="text-sm px-3 py-2 rounded-lg border resize-y"
                    style={{ borderColor: 'var(--border)' }} />
          {error && <p className="text-xs" style={{ color: 'var(--red)' }}>{error}</p>}
          {success && <p className="text-xs" style={{ color: 'var(--green)' }}>{success}</p>}
          <Button onClick={handle} disabled={busy || !selectedSkillId}>
            {busy ? 'Endorsing…' : 'Endorse'}
          </Button>
        </div>
      )}
    </div>
  );
}
