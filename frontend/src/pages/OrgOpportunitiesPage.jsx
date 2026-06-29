import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import {
  getOpportunities, createOpportunity, updateOpportunity,
} from '../api/opportunities';
import { getMyOrganization } from '../api/organizations';
import { getSkills } from '../api/core';
import { Button } from '../components/UI';

// SkillBridge is internship/project-based — no full-time / part-time jobs.
const TYPES = [
  { value: 'internship',     label: 'Internship' },
  { value: 'micro_project',  label: 'Micro Project' },
  { value: 'guided_project', label: 'Guided Project' },
];

const STATUSES = ['draft', 'open', 'closed', 'filled'];


export default function OrgOpportunitiesPage() {
  const navigate = useNavigate();
  const [adding, setAdding] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');

  const { data: org } = useApi(getMyOrganization);
  // Filter by my org's ID so we don't show every opportunity on the platform.
  const { data: opps, loading, error, refetch } = useApi(
    () => org ? getOpportunities({ organization: org.id }) : Promise.resolve([]),
    [org?.id],
  );
  const { data: allSkills } = useApi(getSkills);

  const visible = useMemo(() => {
    const all = opps || [];
    return statusFilter === 'all' ? all : all.filter(o => o.status === statusFilter);
  }, [opps, statusFilter]);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Opportunities</h1>
      <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
        Manage opportunities posted by {org?.name || 'your organization'}.
      </p>

      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2 overflow-x-auto">
          {['all', ...STATUSES].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
                    className="px-3 py-1.5 rounded-full text-xs border capitalize whitespace-nowrap"
                    style={{
                      background: statusFilter === s ? 'var(--text-primary)' : 'white',
                      color: statusFilter === s ? '#fff' : 'var(--text-primary)',
                      borderColor: statusFilter === s ? 'var(--text-primary)' : 'var(--border)',
                    }}>
              {s}
            </button>
          ))}
        </div>
        <button onClick={() => setAdding(o => !o)}
                className="flex items-center gap-1 text-sm font-medium px-3 py-2 rounded-lg border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
          <Plus size={14} /> {adding ? 'Cancel' : 'New opportunity'}
        </button>
      </div>

      {adding && (
        <CreateOpportunityForm
          allSkills={allSkills || []}
          onCreated={() => { setAdding(false); refetch(); }}
        />
      )}

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && visible.length === 0 && (
        <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>
          No opportunities in this status.
        </p>
      )}

      <div className="flex flex-col gap-3">
        {visible.map(op => (
          <OpportunityRow key={op.id} op={op} onChange={refetch}
                          onClick={() => navigate(`/app/org/opportunities/${op.id}`)} />
        ))}
      </div>
    </div>
  );
}


function OpportunityRow({ op, onClick, onChange }) {
  const [busy, setBusy] = useState(false);
  const cycleStatus = async (next) => {
    setBusy(true);
    try {
      await updateOpportunity(op.id, { status: next });
      await onChange();
    } finally { setBusy(false); }
  };
  return (
    <div className="bg-white rounded-2xl p-4 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div onClick={onClick} className="flex-1 min-w-0 cursor-pointer">
          <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>{op.title}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {op.opportunity_type?.replace(/_/g, ' ')} · {op.is_remote ? 'Remote' : (op.location || 'On-site')}
            {op.application_deadline && ` · deadline ${new Date(op.application_deadline).toLocaleDateString()}`}
          </p>
        </div>
        <select value={op.status} onChange={e => cycleStatus(e.target.value)} disabled={busy}
                className="text-xs px-2 py-1 rounded border capitalize"
                style={{ borderColor: 'var(--border)' }}>
          {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
    </div>
  );
}


function CreateOpportunityForm({ allSkills, onCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [opportunityType, setOpportunityType] = useState('internship');
  const [location, setLocation] = useState('');
  const [isRemote, setIsRemote] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [compensation, setCompensation] = useState('');
  const [duration, setDuration] = useState('');
  const [deadline, setDeadline] = useState('');
  const [requiredSkillIds, setRequiredSkillIds] = useState(new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const toggleSkill = (id) => {
    setRequiredSkillIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleCreate = async () => {
    if (!title.trim() || !description.trim()) {
      setError('Title and description are required.');
      return;
    }
    setBusy(true); setError('');
    try {
      await createOpportunity({
        title: title.trim(),
        description: description.trim(),
        opportunity_type: opportunityType,
        location: location.trim(),
        is_remote: isRemote,
        is_paid: isPaid,
        compensation: compensation.trim(),
        duration: duration.trim(),
        application_deadline: deadline ? new Date(deadline).toISOString() : null,
        required_skill_ids: Array.from(requiredSkillIds),
      });
      onCreated();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="bg-white rounded-2xl p-5 border mb-5" style={{ borderColor: 'var(--border)' }}>
      <p className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>New opportunity</p>
      <div className="flex flex-col gap-2">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title"
               className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
        <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                  placeholder="Description (what the role/project involves)"
                  className="px-3 py-2 text-sm rounded-lg border resize-y"
                  style={{ borderColor: 'var(--border)' }} />
        <select value={opportunityType} onChange={e => setOpportunityType(e.target.value)}
                className="px-3 py-2 text-sm rounded-lg border"
                style={{ borderColor: 'var(--border)' }}>
          {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <input value={location} onChange={e => setLocation(e.target.value)} placeholder="Location (e.g. Lagos)"
               className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
        <div className="flex gap-4 text-sm">
          <label className="flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <input type="checkbox" checked={isRemote} onChange={e => setIsRemote(e.target.checked)} /> Remote
          </label>
          <label className="flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <input type="checkbox" checked={isPaid} onChange={e => setIsPaid(e.target.checked)} /> Paid
          </label>
        </div>
        {isPaid && (
          <input value={compensation} onChange={e => setCompensation(e.target.value)}
                 placeholder="Compensation (e.g. ₦150,000/month)"
                 className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
        )}
        <input value={duration} onChange={e => setDuration(e.target.value)}
               placeholder="Duration (e.g. 3 months)"
               className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
        <div>
          <label className="block text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Application deadline</label>
          <input type="datetime-local" value={deadline} onChange={e => setDeadline(e.target.value)}
                 className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
        </div>

        <div>
          <p className="text-xs mb-2 mt-2" style={{ color: 'var(--text-muted)' }}>Required skills</p>
          <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto">
            {allSkills.map(s => {
              const active = requiredSkillIds.has(s.id);
              return (
                <button key={s.id} type="button" onClick={() => toggleSkill(s.id)}
                        className="px-2.5 py-1 rounded-full text-xs border"
                        style={{
                          background: active ? 'var(--text-primary)' : 'transparent',
                          color: active ? '#fff' : 'var(--text-primary)',
                          borderColor: active ? 'var(--text-primary)' : 'var(--border)',
                        }}>
                  {s.name}
                </button>
              );
            })}
          </div>
        </div>

        {error && <p className="text-xs" style={{ color: 'var(--red)' }}>{error}</p>}
        <Button onClick={handleCreate} disabled={busy}>
          {busy ? 'Creating…' : 'Create as draft'}
        </Button>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          New opportunities start as draft. Set status to "open" to publish.
        </p>
      </div>
    </div>
  );
}
