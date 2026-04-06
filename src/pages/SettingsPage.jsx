import { useNavigate } from 'react-router-dom';
import { User, Lock, Shield, ChevronRight, LogOut } from 'lucide-react';

const settingsItems = [
  { icon: User, label: 'My Profile', path: '/app/profile' },
  { icon: Lock, label: 'Change Password', path: '/app/settings/password' },
  { icon: Shield, label: 'Privacy Policy', path: '/app/settings/privacy' },
];

export default function SettingsPage() {
  const navigate = useNavigate();

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-8" style={{ color: 'var(--text-primary)' }}>Settings</h1>

      <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
        {settingsItems.map(({ icon: Icon, label, path }, i) => (
          <button
            key={label}
            onClick={() => navigate(path)}
            className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left"
            style={{ borderBottom: i < settingsItems.length - 1 ? '1px solid var(--border)' : 'none' }}
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg)' }}>
                <Icon size={18} style={{ color: 'var(--text-secondary)' }} />
              </div>
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{label}</span>
            </div>
            <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
          </button>
        ))}
      </div>

      {/* Logout */}
      <div className="bg-white rounded-2xl border mt-4 overflow-hidden" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={() => navigate('/sign-in')}
          className="w-full flex items-center gap-3 px-5 py-4 hover:bg-red-50 transition-colors"
        >
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#FEE2E2' }}>
            <LogOut size={18} style={{ color: '#EF4444' }} />
          </div>
          <span className="text-sm font-medium" style={{ color: '#EF4444' }}>Log Out</span>
        </button>
      </div>
    </div>
  );
}
