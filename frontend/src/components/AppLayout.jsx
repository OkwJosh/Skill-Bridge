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
  const items = [{ to: '/app/home', icon: '/icons/nav_home.svg', label: 'Home' }];

  if (isTalent) {
    items.push({ to: '/app/jobs',            icon: '/icons/opportunities.svg', label: 'Opportunities' });
    items.push({ to: '/app/my-applications', icon: FileText,  label: 'My Applications' });
  }
  if (isMentor) {
    items.push({ to: '/app/mentor/mentorships', icon: '/icons/calender.svg', label: 'My Mentorships' });
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
    items.push({ to: '/app/talent', icon: '/icons/talent.svg', label: 'Talents' });
  }
  if (!isSchoolAdmin) {
    items.push({ to: '/app/search', icon: '/icons/search_icon.svg', label: 'Search' });
  }
  items.push({ to: '/app/notifications', icon: '/icons/nav_alerts.svg', label: 'Notifications' });
  items.push({ to: '/app/settings',      icon: '/icons/settings.svg', label: 'Settings' });
  return items;
}

export function Avatar({ name, size = 40, className = '', imageUrl = null }) {
  if (imageUrl) {
    return (
      <img src={imageUrl} alt={name} className={`rounded-full object-cover shrink-0 ${className}`} 
           style={{ width: size, height: size }} />
    );
  }
  // Fallback if no specific image is provided
  return (
    <img src="/icons/male_image_fallback.png" alt={name || 'User'} className={`rounded-full object-cover shrink-0 ${className}`} 
         style={{ width: size, height: size, background: '#D1D5DB' }} />
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
            <img src="/logos/logo.svg" alt="SkillBridge Logo" className="w-8 h-8 object-contain" />
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
                  {({ isActive }) => (
                    <>
                      {typeof Icon === 'string' ? (
                        <img src={Icon} alt={label} style={{ width: 18, height: 18, filter: isActive ? 'brightness(0) invert(1)' : 'none' }} />
                      ) : (
                        <Icon size={18} />
                      )}
                      <span className="flex-1">{label}</span>
                      {isNotifications && unread > 0 && (
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full text-white"
                              style={{ background: 'var(--red)' }}>
                          {unread > 99 ? '99+' : unread}
                        </span>
                      )}
                    </>
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
            <Avatar name={user?.full_name || 'User'} size={32} imageUrl={user?.avatar_url} />
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
