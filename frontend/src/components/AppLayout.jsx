import { useEffect, useState } from 'react';
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  Home, Search, Briefcase, Users, Bell, Settings, LogOut, FileText,
  Calendar, Building2, GraduationCap, ClipboardList,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getUnreadNotificationCount } from '../api/notifications';
import { resendVerificationEmail } from '../api/auth';

// Role-aware side-nav.
//   Talent      : Home · Opportunities · My Applications · Search · Notifications · Settings
//   Mentor      : Home · My Mentorships · Talents · Search · Notifications · Settings
//   Org Admin   : Home · Organization · My Opportunities · Talents · Search · Notifications · Settings
//   School Admin: Home · School · Roster · Notifications · Settings
function buildNavItems({ isTalent, isMentor, isOrgAdmin, isSchoolAdmin }) {
  const items = [{ to: '/app/home', icon: Home, label: 'Home' }];

  if (isTalent) {
    items.push({ to: '/app/jobs',            icon: Briefcase, label: 'Opportunities' });
    items.push({ to: '/app/my-applications', icon: FileText,  label: 'My Applications' });
  }
  if (isMentor) {
    items.push({ to: '/app/mentor/mentorships', icon: Calendar, label: 'My Mentorships' });
  }
  if (isOrgAdmin) {
    items.push({ to: '/app/org/profile',       icon: Building2,     label: 'Organization' });
    items.push({ to: '/app/org/opportunities', icon: ClipboardList, label: 'My Opportunities' });
  }
  if (isSchoolAdmin) {
    items.push({ to: '/app/school',        icon: GraduationCap, label: 'School' });
    items.push({ to: '/app/school/roster', icon: FileText,      label: 'Roster' });
  }
  if (isMentor || isOrgAdmin) {
    items.push({ to: '/app/talent', icon: Users, label: 'Talents' });
  }
  if (!isSchoolAdmin) {
    items.push({ to: '/app/search', icon: Search, label: 'Search' });
  }
  items.push({ to: '/app/notifications', icon: Bell,     label: 'Notifications' });
  items.push({ to: '/app/settings',      icon: Settings, label: 'Settings' });
  return items;
}

export function Avatar({ name, size = 40, className = '' }) {
  const initials = name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?';
  return (
    <div className={`rounded-full flex items-center justify-center shrink-0 font-medium ${className}`}
      style={{ width: size, height: size, background: '#D1D5DB', color: '#374151', fontSize: size * 0.35 }}>
      {initials}
    </div>
  );
}

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isTalent, isMentor, isOrgAdmin } = useAuth();
  const isSchoolAdmin = user?.is_school_admin ?? false;
  const navItems = buildNavItems({ isTalent, isMentor, isOrgAdmin, isSchoolAdmin });

  // Lightweight unread-count poll. Refreshes when the user navigates
  // (so opening the page clears the badge) and every 60s while idle.
  const [unread, setUnread] = useState(0);
  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const res = await getUnreadNotificationCount();
        if (!cancelled) setUnread(res?.unread_count ?? 0);
      } catch { /* non-fatal */ }
    };
    tick();
    const id = setInterval(tick, 60_000);
    return () => { cancelled = true; clearInterval(id); };
  }, [location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/sign-in');
  };

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--bg)' }}>
      <aside className="w-56 flex flex-col justify-between py-6 px-4 shrink-0" style={{ background: 'var(--bg)' }}>
        {/* Logo */}
        <div>
          <div className="flex items-center gap-2 px-3 mb-8">
            <svg width="24" height="24" viewBox="0 0 40 40" fill="none">
              <path d="M20 8C14 8 8 12 8 18C8 22 11 25 15 26L20 32L25 26C29 25 32 22 32 18C32 12 26 8 20 8Z" fill="#1A1A1A"/>
              <path d="M14 20C14 20 17 24 20 24C23 24 26 20 26 20" stroke="white" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span className="font-semibold text-base" style={{ color: 'var(--text-primary)' }}>SkillBridge</span>
          </div>

          <nav className="flex flex-col gap-1">
            {navItems.map(({ to, icon: Icon, label }) => {
              const isNotifications = to === '/app/notifications';
              return (
                <NavLink key={to} to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${isActive ? 'text-white' : 'hover:bg-black/5'}`
                  }
                  style={({ isActive }) => isActive
                    ? { background: 'var(--text-primary)', color: '#fff' }
                    : { color: 'var(--text-secondary)' }
                  }>
                  <Icon size={18} />
                  <span className="flex-1">{label}</span>
                  {isNotifications && unread > 0 && (
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full text-white"
                          style={{ background: 'var(--red)' }}>
                      {unread > 99 ? '99+' : unread}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* User + Logout */}
        <div>
          <button onClick={() => navigate('/app/profile')}
            className="flex items-center gap-2 px-3 py-2 mb-1 w-full rounded-xl hover:bg-black/5 transition-colors text-left">
            <Avatar name={user?.full_name || 'User'} size={32} />
            <div className="min-w-0">
              <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {user?.roles?.[0] || 'Member'}
              </p>
            </div>
          </button>
          <button onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium w-full rounded-lg hover:bg-red-50 transition-colors"
            style={{ color: '#EF4444' }}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        {user && user.email_verified === false && <EmailVerificationBanner />}
        <Outlet />
      </main>
    </div>
  );
}


function EmailVerificationBanner() {
  const [state, setState] = useState('idle'); // idle | sending | sent | error
  const [message, setMessage] = useState('');
  const handleResend = async () => {
    setState('sending');
    try {
      const res = await resendVerificationEmail();
      setState('sent'); setMessage(res?.message || 'Verification email sent.');
    } catch (err) {
      setState('error'); setMessage(err.message);
    }
  };
  return (
    <div className="px-6 py-2 text-sm flex items-center justify-between gap-3"
         style={{ background: '#FEF3C7', color: '#92400E' }}>
      <span>
        Please verify your email. We sent you a link — check your inbox (and spam folder).
      </span>
      <div className="flex items-center gap-3">
        {message && <span className="text-xs">{message}</span>}
        <button onClick={handleResend} disabled={state === 'sending'}
                className="text-xs font-semibold underline disabled:opacity-50">
          {state === 'sending' ? 'Sending…' : 'Resend'}
        </button>
      </div>
    </div>
  );
}
