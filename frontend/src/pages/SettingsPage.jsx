import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User, Lock, ChevronRight, LogOut, Users, Calendar, Building2, GraduationCap,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { requestPasswordReset } from '../api/auth';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { logout, user, isTalent, isMentor, isOrgAdmin } = useAuth();
  const isSchoolAdmin = user?.is_school_admin ?? false;
  const [passwordMsg, setPasswordMsg] = useState('');
  const [passwordBusy, setPasswordBusy] = useState(false);

  const handleChangePassword = async () => {
    if (!user?.email) return;
    setPasswordBusy(true); setPasswordMsg('');
    try {
      await requestPasswordReset(user.email);
      setPasswordMsg(`Reset link sent to ${user.email}. Check your inbox.`);
    } catch (err) {
      setPasswordMsg(err.message);
    } finally {
      setPasswordBusy(false);
    }
  };

  // Role-specific shortcuts. A multi-role user sees one row per role.
  const roleItems = [];
  if (isTalent) {
    roleItems.push({ icon: Users, label: 'My Mentors', action: () => navigate('/app/my-mentors') });
  }
  if (isMentor) {
    roleItems.push({ icon: Calendar, label: 'My Mentees', action: () => navigate('/app/mentor/mentorships') });
  }
  if (isOrgAdmin) {
    roleItems.push({ icon: Building2, label: 'My Organization', action: () => navigate('/app/org/profile') });
  }
  if (isSchoolAdmin) {
    roleItems.push({ icon: GraduationCap, label: 'My School', action: () => navigate('/app/school') });
  }

  const settingsItems = [
    { icon: User, label: 'My Profile', action: () => navigate('/app/profile') },
    ...roleItems,
    {
      icon: Lock,
      label: passwordBusy ? 'Sending…' : 'Change Password',
      action: handleChangePassword,
    },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/sign-in');
  };

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-8" style={{ color: 'var(--text-primary)' }}>Settings</h1>

      {/* User info chip */}
      <div className="bg-white rounded-2xl p-4 flex items-center gap-3 mb-4 border" style={{ borderColor: 'var(--border)' }}>
        <div className="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm"
          style={{ background: '#D1D5DB', color: '#374151' }}>
          {user?.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?'}
        </div>
        <div>
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{user?.full_name || 'User'}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user?.email}</p>
        </div>
      </div>

      {/* Settings list */}
      <div className="bg-white rounded-2xl border overflow-hidden mb-2" style={{ borderColor: 'var(--border)' }}>
        {settingsItems.map(({ icon: Icon, label, action }, i) => (
          <button key={label} onClick={action} disabled={passwordBusy && label === 'Sending…'}
            className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left"
            style={{ borderBottom: i < settingsItems.length - 1 ? '1px solid var(--border)' : 'none' }}>
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
      {passwordMsg && (
        <p className="text-xs mb-4 px-2" style={{ color: 'var(--text-secondary)' }}>{passwordMsg}</p>
      )}

      {/* Logout */}
      <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
        <button onClick={handleLogout}
          className="w-full flex items-center gap-3 px-5 py-4 hover:bg-red-50 transition-colors">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#FEE2E2' }}>
            <LogOut size={18} style={{ color: '#EF4444' }} />
          </div>
          <span className="text-sm font-medium" style={{ color: '#EF4444' }}>Log Out</span>
        </button>
      </div>
    </div>
  );
}
