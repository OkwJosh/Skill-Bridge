import { useState } from 'react';
import { notifications } from '../data';
import { Briefcase, CheckCircle, Star, Heart, Bell, User } from 'lucide-react';

const iconMap = {
  briefcase: Briefcase,
  check: CheckCircle,
  star: Star,
  heart: Heart,
  bell: Bell,
  user: User,
};

export default function NotificationsPage() {
  const [items, setItems] = useState(notifications);

  const markRead = (id) => {
    setItems(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const groups = ['Today', 'Yesterday', 'Earlier'];

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Notifications</h1>
        <button
          onClick={() => setItems(prev => prev.map(n => ({ ...n, read: true })))}
          className="text-sm" style={{ color: 'var(--text-muted)' }}
        >
          Mark all read
        </button>
      </div>

      {groups.map(group => {
        const groupItems = items.filter(n => n.group === group);
        if (!groupItems.length) return null;
        return (
          <div key={group} className="mb-6">
            <p className="text-sm mb-3 font-medium" style={{ color: 'var(--text-muted)' }}>{group}</p>
            <div className="flex flex-col gap-2">
              {groupItems.map(notif => {
                const Icon = iconMap[notif.icon] || Bell;
                return (
                  <div
                    key={notif.id}
                    onClick={() => markRead(notif.id)}
                    className="bg-white rounded-2xl p-4 flex items-start gap-3 cursor-pointer hover:shadow-sm transition-shadow border"
                    style={{ borderColor: notif.read ? 'var(--border)' : 'var(--text-primary)' }}
                  >
                    <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0" style={{ background: '#F3F4F6' }}>
                      <Icon size={18} style={{ color: 'var(--text-secondary)' }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{notif.title}</p>
                      <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>{notif.message}</p>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{notif.time}</p>
                    </div>
                    {!notif.read && (
                      <div className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ background: '#EF4444' }} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
