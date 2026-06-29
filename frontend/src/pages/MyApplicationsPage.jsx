import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { getMyApplications } from '../api/opportunities';

const STATUSES = ['all', 'pending', 'reviewing', 'shortlisted', 'accepted', 'rejected', 'withdrawn'];
const STATUS_COLORS = {
  pending:    { bg: '#FEF3C7', fg: '#92400E' },
  reviewing:  { bg: '#DBEAFE', fg: '#1E40AF' },
  shortlisted:{ bg: '#E0E7FF', fg: '#3730A3' },
  accepted:   { bg: '#D1FAE5', fg: '#065F46' },
  rejected:   { bg: '#FEE2E2', fg: '#991B1B' },
  withdrawn:  { bg: '#F3F4F6', fg: '#374151' },
};

export default function MyApplicationsPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('all');
  const { data: applications, loading, error, refetch } = useApi(getMyApplications);

  const filtered = useMemo(() => {
    const all = applications || [];
    return statusFilter === 'all' ? all : all.filter(a => a.status === statusFilter);
  }, [applications, statusFilter]);

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>My Applications</h1>

      {/* Status filter chips */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {STATUSES.map(s => (
          <button key={s} onClick={() => setStatusFilter(s)}
                  className="px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-all capitalize"
                  style={{
                    background: statusFilter === s ? 'var(--text-primary)' : 'white',
                    color: statusFilter === s ? '#fff' : 'var(--text-primary)',
                    borderColor: statusFilter === s ? 'var(--text-primary)' : 'var(--border)',
                  }}>
            {s}
          </button>
        ))}
      </div>

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-12">
          <p style={{ color: 'var(--text-muted)' }} className="mb-3">
            {statusFilter === 'all'
              ? "You haven't applied to any opportunities yet."
              : `No applications with status "${statusFilter}".`}
          </p>
          {statusFilter === 'all' && (
            <button onClick={() => navigate('/app/jobs')}
                    className="text-sm font-semibold underline"
                    style={{ color: 'var(--text-primary)' }}>
              Browse opportunities →
            </button>
          )}
        </div>
      )}

      <div className="flex flex-col gap-3">
        {filtered.map(app => {
          const c = STATUS_COLORS[app.status] || STATUS_COLORS.pending;
          const op = app.opportunity || {};
          const poster = op.organization_name || op.poster_name || '—';
          const typeLabel = TYPE_LABELS[op.opportunity_type] || op.opportunity_type;
          const place = op.location || (op.is_remote ? 'Remote' : null);
          return (
            <div key={app.id}
                 onClick={() => op.id && navigate(`/app/jobs/${op.id}`)}
                 className="bg-white rounded-2xl p-4 border cursor-pointer hover:shadow-md transition-shadow"
                 style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="min-w-0">
                  <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                    {op.title || 'Opportunity'}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{poster}</p>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full font-medium capitalize shrink-0"
                      style={{ background: c.bg, color: c.fg }}>
                  {app.status}
                </span>
              </div>

              {/* Detail chips */}
              <div className="flex flex-wrap gap-1.5 mb-2">
                {typeLabel && <DetailChip>{typeLabel}</DetailChip>}
                {place && <DetailChip>{place}</DetailChip>}
                {op.compensation && <DetailChip>{op.compensation}</DetailChip>}
                {!op.compensation && op.is_paid === false && <DetailChip>Unpaid</DetailChip>}
                {op.duration && <DetailChip>{op.duration}</DetailChip>}
              </div>

              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Applied {new Date(app.created_at).toLocaleDateString()}
                {app.reviewed_at && ` · Reviewed ${new Date(app.reviewed_at).toLocaleDateString()}`}
                {op.application_deadline &&
                  ` · Closes ${new Date(op.application_deadline).toLocaleDateString()}`}
              </p>

              {app.cover_letter && (
                <p className="text-xs mt-2 line-clamp-2" style={{ color: 'var(--text-secondary)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Your note: </span>
                  {app.cover_letter}
                </p>
              )}
              {app.reviewer_notes && (
                <p className="text-xs mt-2 italic" style={{ color: 'var(--text-secondary)' }}>
                  Reviewer: "{app.reviewer_notes}"
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const TYPE_LABELS = {
  internship: 'Internship',
  micro_project: 'Micro-Project',
  guided_project: 'Guided Project',
};

function DetailChip({ children }) {
  return (
    <span className="text-xs px-2 py-0.5 rounded-full capitalize"
          style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
      {children}
    </span>
  );
}
