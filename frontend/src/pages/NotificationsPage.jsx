import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import {
  listNotifications, markNotificationRead, markAllNotificationsRead,
} from '../api/notifications';
import {
  Bell, Briefcase, Award, CalendarCheck, GraduationCap, Sparkles,
} from 'lucide-react';

const ICON_BY_KIND = {
  application_submitted: Briefcase,
  application_status_changed: Briefcase,
  skill_endorsed: Award,
  mentorship_created: Sparkles,
  mentor_session_scheduled: CalendarCheck,
  school_verified: GraduationCap,
  generic: Bell,
};

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all'); // all | unread

  const { data, loading, error, refetch } = useApi(
    () => listNotifications(filter === 'unread' ? { is_read: false } : {}),
    [filter],
  );

  const items = data?.items || [];
  const unreadCount = data?.unread_count ?? 0;

  const handleClick = async (n) => {
    if (!n.is_read) {
      try { await markNotificationRead(n.id); } catch {/* non-fatal */}
    }
    if (n.link_url) {
      navigate(n.link_url);
    } else {
      refetch();
    }
  };

  const handleMarkAll = async () => {
    try { await markAllNotificationsRead(); } catch {/* non-fatal */}
    refetch();
  };

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center justify-between mb-6 gap-3 flex-wrap">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Notifications {unreadCount > 0 && (
            <span className="ml-2 text-sm font-medium px-2 py-0.5 rounded-full text-white"
                  style={{ background: 'var(--red)' }}>
              {unreadCount}
            </span>
          )}
        </h1>
        <div className="flex items-center gap-2">
          {['all', 'unread'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
                    className="px-3 py-1 rounded-full text-xs border capitalize"
                    style={{
                      background:  filter === f ? 'var(--text-primary)' : 'white',
                      color:       filter === f ? '#fff' : 'var(--text-primary)',
                      borderColor: filter === f ? 'var(--text-primary)' : 'var(--border)',
                    }}>
              {f}
            </button>
          ))}
          {unreadCount > 0 && (
            <button onClick={handleMarkAll}
                    className="text-xs font-medium underline"
                    style={{ color: 'var(--text-secondary)' }}>
              Mark all read
            </button>
          )}
        </div>
      </div>

      {loading && <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && items.length === 0 && (
        <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>
          {filter === 'unread' ? 'No unread notifications.' : 'No notifications yet.'}
        </p>
      )}

      <div className="flex flex-col gap-3">
        {items.map(n => {
          const Icon = ICON_BY_KIND[n.kind] || Bell;
          return (
            <button key={n.id} onClick={() => handleClick(n)}
                    className="flex items-start gap-4 p-4 rounded-2xl border text-left transition-colors hover:bg-gray-50"
                    style={{ background: 'white',
                             borderColor: n.is_read ? 'var(--border)' : 'var(--text-primary)' }}>
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                   style={{ background: 'var(--bg)' }}>
                <Icon size={18} style={{ color: 'var(--text-secondary)' }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{n.title}</p>
                {n.body && (
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>{n.body}</p>
                )}
                <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                  {new Date(n.created_at).toLocaleString()}
                </p>
              </div>
              {!n.is_read && (
                <div className="w-2 h-2 rounded-full shrink-0 mt-1.5" style={{ background: 'var(--red)' }} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
