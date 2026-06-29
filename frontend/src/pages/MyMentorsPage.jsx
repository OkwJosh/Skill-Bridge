/**
 * MyMentorsPage — talent-side view of their mentorships.
 *
 * Reads GET /talents/me/mentorships/ (read-only for talents). Lets a
 * talent see who is mentoring them, the focus area, and status.
 */

import { useApi } from '../hooks/useApi';
import { listMyMentorshipsAsTalent } from '../api/talents';
import { Avatar, PageHeader } from '../components/UI';
import { Users } from 'lucide-react';

export default function MyMentorsPage() {
  const { data: mentorships, loading, error } = useApi(listMyMentorshipsAsTalent);
  const items = mentorships || [];

  return (
    <div className="p-8 max-w-3xl">
      <PageHeader title="My Mentors" onBack />

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && items.length === 0 && (
        <div className="text-center py-12">
          <Users size={32} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>
            You don't have any mentors yet. A mentor can add you from their dashboard.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map(m => {
          const name = m.mentor?.full_name || m.mentor?.email || 'Mentor';
          return (
            <div key={m.id}
                 className="bg-white rounded-2xl p-5 border"
                 style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-start gap-3 mb-2">
                <Avatar name={name} size={42} />
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                    {name}
                    {m.mentor?.is_verified && (
                      <span title="Verified mentor" className="ml-1" style={{ color: 'var(--green)' }}>✓</span>
                    )}
                  </p>
                  <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                    {m.mentor?.headline || '—'}
                  </p>
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full capitalize shrink-0"
                      style={{
                        background: m.status === 'active' ? '#D1FAE5'
                                  : m.status === 'paused' ? '#FEF3C7' : '#F3F4F6',
                        color:      m.status === 'active' ? '#065F46'
                                  : m.status === 'paused' ? '#92400E' : '#374151',
                      }}>
                  {m.status}
                </span>
              </div>
              {m.focus_area && (
                <p className="text-xs italic mt-2" style={{ color: 'var(--text-secondary)' }}>
                  "{m.focus_area}"
                </p>
              )}
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                Since {new Date(m.started_at).toLocaleDateString()}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
