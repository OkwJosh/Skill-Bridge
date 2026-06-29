import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sparkles, Search } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useAIInsight } from '../hooks/useAIInsight';
import {
  getOpportunity, listOpportunityApplications, updateApplicationStatus,
} from '../api/opportunities';
import { getOpportunityTalentMatches, getProactiveSourcing } from '../api/ai';
import { getMyOrganization } from '../api/organizations';
import { Avatar, Button, PageHeader } from '../components/UI';


const APP_STATUSES = ['pending', 'reviewing', 'shortlisted', 'accepted', 'rejected'];


export default function OrgOpportunityDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: op, loading: opLoading, error: opError } = useApi(
    () => getOpportunity(id), [id],
  );

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader title={op?.title || 'Opportunity'} onBack />

      {opLoading && <p style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {opError && <p style={{ color: 'var(--red)' }}>{opError}</p>}

      {op && (
        <>
          {/* Summary */}
          <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                    style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
                {op.status}
              </span>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Posted {new Date(op.created_at).toLocaleDateString()}
              </p>
            </div>
            <p className="text-sm mb-3" style={{ color: 'var(--text-primary)' }}>{op.description}</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {op.opportunity_type?.replace(/_/g, ' ')}
              {op.is_remote ? ' · Remote' : op.location ? ` · ${op.location}` : ''}
              {op.is_paid && op.compensation ? ` · ${op.compensation}` : ''}
              {op.application_deadline && ` · deadline ${new Date(op.application_deadline).toLocaleDateString()}`}
            </p>
          </div>

          <ApplicationsSection opportunityId={op.id} />

          {/* AI Talent Matches for THIS opportunity */}
          <TalentMatchesSection opportunityId={op.id} />

          {/* Predictive Sourcing across whole org */}
          <ProactiveSourcingSection navigate={navigate} />
        </>
      )}
    </div>
  );
}


// ── Applications inbox ─────────────────────────────────────────────────────
function ApplicationsSection({ opportunityId }) {
  const [statusFilter, setStatusFilter] = useState('all');
  const { data: apps, loading, refetch } = useApi(
    () => listOpportunityApplications(opportunityId, statusFilter === 'all' ? null : statusFilter),
    [opportunityId, statusFilter],
  );

  return (
    <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Applications</p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-3">
        {['all', ...APP_STATUSES].map(s => (
          <button key={s} onClick={() => setStatusFilter(s)}
                  className="px-3 py-1 rounded-full text-xs border capitalize whitespace-nowrap"
                  style={{
                    background: statusFilter === s ? 'var(--text-primary)' : 'white',
                    color: statusFilter === s ? '#fff' : 'var(--text-primary)',
                    borderColor: statusFilter === s ? 'var(--text-primary)' : 'var(--border)',
                  }}>
            {s}
          </button>
        ))}
      </div>

      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {!loading && (apps || []).length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No applications in this status.</p>
      )}

      <div className="flex flex-col gap-2">
        {(apps || []).map(a => <ApplicationRow key={a.id} app={a} onChange={refetch} />)}
      </div>
    </div>
  );
}

function ApplicationRow({ app, onChange }) {
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(app.status);
  const [notes, setNotes] = useState(app.reviewer_notes || '');
  const [editing, setEditing] = useState(false);

  const save = async () => {
    setBusy(true);
    try {
      await updateApplicationStatus(app.id, { status, reviewer_notes: notes });
      setEditing(false);
      await onChange();
    } finally { setBusy(false); }
  };

  return (
    <div className="border rounded-lg p-3" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-start gap-3">
        <Avatar name={app.talent?.full_name || app.talent?.email || '—'} size={36} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {app.talent?.full_name || app.talent?.email || `Talent #${app.talent_id ?? '?'}`}
            </p>
            {editing ? (
              <select value={status} onChange={e => setStatus(e.target.value)}
                      className="text-xs px-2 py-1 rounded border capitalize" style={{ borderColor: 'var(--border)' }}>
                {APP_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            ) : (
              <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                    style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
                {app.status}
              </span>
            )}
          </div>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            Applied {new Date(app.created_at).toLocaleDateString()}
          </p>
          {app.cover_letter && (
            <p className="text-xs mt-2 italic" style={{ color: 'var(--text-secondary)' }}>
              "{app.cover_letter}"
            </p>
          )}
          {editing ? (
            <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2}
                      placeholder="Reviewer notes"
                      className="w-full text-xs mt-2 px-2 py-1 border rounded"
                      style={{ borderColor: 'var(--border)' }} />
          ) : app.reviewer_notes ? (
            <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
              <strong>Notes:</strong> {app.reviewer_notes}
            </p>
          ) : null}
          <div className="flex gap-2 mt-2">
            {editing ? (
              <>
                <Button onClick={save} disabled={busy}>{busy ? 'Saving…' : 'Save'}</Button>
                <button onClick={() => { setEditing(false); setStatus(app.status); setNotes(app.reviewer_notes || ''); }}
                        className="text-xs" style={{ color: 'var(--text-muted)' }}>Cancel</button>
              </>
            ) : (
              <button onClick={() => setEditing(true)} className="text-xs underline"
                      style={{ color: 'var(--text-primary)' }}>Review</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


// ── AI Talent Matches ──────────────────────────────────────────────────────
function TalentMatchesSection({ opportunityId }) {
  const navigate = useNavigate();
  const { data, loading, error, aiDisabled } = useAIInsight(
    () => getOpportunityTalentMatches(opportunityId),
    [opportunityId],
  );
  if (aiDisabled) return null;
  const matches = data?.matches || [];

  return (
    <div className="bg-white rounded-2xl p-5 border mb-6" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-3">
        <Sparkles size={16} style={{ color: 'var(--text-secondary)' }} />
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          AI Talent Matches for this opportunity
        </p>
      </div>
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Ranking talents…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {!loading && matches.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          No matches yet. Make sure the opportunity has required skills set.
        </p>
      )}
      <div className="flex flex-col gap-2">
        {matches.slice(0, 5).map(m => (
          <div key={m.talent_id}
               onClick={() => navigate(`/app/talent/${m.talent_id}`)}
               className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50"
               style={{ borderColor: 'var(--border)' }}>
            <div className="flex items-center gap-3">
              <Avatar name={m.talent?.full_name} size={36} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {m.talent?.full_name} <span className="text-xs" style={{ color: 'var(--text-muted)' }}>· fit {m.fit_score}</span>
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{m.reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ── Predictive Sourcing ────────────────────────────────────────────────────
function ProactiveSourcingSection({ navigate }) {
  const { data: org } = useApi(getMyOrganization);
  const orgId = org?.id;
  const { data, loading, error, aiDisabled } = useAIInsight(
    () => orgId ? getProactiveSourcing(orgId) : Promise.resolve(null),
    [orgId],
  );
  if (aiDisabled) return null;
  const matches = data?.matches || [];

  return (
    <div className="bg-white rounded-2xl p-5 border" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Search size={16} style={{ color: 'var(--text-secondary)' }} />
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Proactive Sourcing — hidden gems
          </p>
        </div>
        {data?.confidence && (
          <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                style={{
                  background: data.confidence === 'medium' ? '#DBEAFE' : '#FEF3C7',
                  color: data.confidence === 'medium' ? '#1E40AF' : '#92400E',
                }}>
            {data.confidence} confidence
          </span>
        )}
      </div>
      {data?.confidence_reason && (
        <p className="text-xs mb-3 italic" style={{ color: 'var(--text-muted)' }}>{data.confidence_reason}</p>
      )}
      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Finding candidates…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}
      {!loading && matches.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          No suggestions yet. Accept or shortlist more applicants to improve recommendations.
        </p>
      )}
      <div className="flex flex-col gap-2">
        {matches.slice(0, 5).map(m => (
          <div key={m.talent_id}
               onClick={() => navigate(`/app/talent/${m.talent_id}`)}
               className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50"
               style={{ borderColor: 'var(--border)' }}>
            <div className="flex items-center gap-3">
              <Avatar name={m.talent?.full_name} size={36} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {m.talent?.full_name} <span className="text-xs" style={{ color: 'var(--text-muted)' }}>· fit {m.fit_score}</span>
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{m.reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
