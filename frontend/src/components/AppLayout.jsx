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

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-56 flex-col justify-between py-6 px-4 shrink-0 border-r" style={{ background: 'var(--bg)', borderColor: 'var(--border)' }}>
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

      {/* Main Content */}
      <main className="flex-1 w-full overflow-y-auto pb-20 md:pb-0 relative">
        {user && user.email_verified === false && <EmailVerificationBanner />}
        
        {/* Mobile Header (replaces standard HomePage header branding on mobile if needed, but we keep it simple here) */}
        <div className="md:hidden flex items-center justify-between px-5 py-4 border-b bg-white/80 backdrop-blur-md sticky top-0 z-30" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center gap-2">
            <img src="/logos/logo.svg" alt="SkillBridge Logo" className="w-7 h-7 object-contain" />
            <span className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>SkillBridge</span>
          </div>
          <button onClick={() => setMobileMenuOpen(true)}>
            <img src="/icons/nav_alerts.svg" alt="Menu" style={{ width: 22, height: 22, filter: 'brightness(0)' }} />
            {/* Using a simple menu icon fallback if needed, or we can just use the avatar */}
            <Avatar name={user?.full_name || 'User'} size={32} imageUrl={user?.avatar_url} />
          </button>
        </div>

        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 w-full bg-white border-t z-40 flex justify-around items-center px-2 py-2 pb-safe" style={{ borderColor: 'var(--border)' }}>
        {navItems.slice(0, 4).map(({ to, icon: Icon, label }) => {
          const isNotifications = to === '/app/notifications';
          return (
            <NavLink key={to} to={to}
              className="flex flex-col items-center justify-center w-full py-1 gap-1 relative"
              style={({ isActive }) => ({ color: isActive ? 'var(--text-primary)' : 'var(--text-muted)' })}>
              {({ isActive }) => (
                <>
                  {typeof Icon === 'string' ? (
                    <img src={Icon} alt={label} style={{ width: 22, height: 22, filter: isActive ? 'brightness(0)' : 'brightness(0) opacity(0.4)' }} />
                  ) : (
                    <Icon size={22} color={isActive ? 'var(--text-primary)' : 'var(--text-muted)'} />
                  )}
                  <span className="text-[10px] font-medium truncate w-full text-center">{label}</span>
                  {isNotifications && unread > 0 && (
                    <span className="absolute top-0 right-1/4 translate-x-2 -translate-y-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
        {/* Mobile Menu Toggle Button */}
        <button onClick={() => setMobileMenuOpen(true)} className="flex flex-col items-center justify-center w-full py-1 gap-1 text-gray-400 hover:text-black">
          <Settings size={22} />
          <span className="text-[10px] font-medium truncate w-full text-center">More</span>
        </button>
      </nav>

      {/* Mobile Drawer (More Items) */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="w-64 bg-white h-full shadow-2xl relative flex flex-col pt-12 pb-6 px-4 animate-slide-in-right">
            <button onClick={() => setMobileMenuOpen(false)} className="absolute top-4 right-4 p-2 text-gray-400 hover:text-black">
              <LogOut size={20} className="rotate-180" />
            </button>
            <div className="mb-8 px-2 flex items-center gap-3">
              <Avatar name={user?.full_name || 'User'} size={44} imageUrl={user?.avatar_url} />
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{user?.full_name}</p>
                <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{user?.roles?.[0]}</p>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto flex flex-col gap-2">
              {navItems.map(({ to, icon: Icon, label }) => (
                <NavLink key={to} to={to} onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all ${isActive ? 'bg-gray-100 text-black' : 'text-gray-500'}`}>
                  {typeof Icon === 'string' ? <img src={Icon} style={{ width: 18, height: 18 }} /> : <Icon size={18} />}
                  {label}
                </NavLink>
              ))}
            </div>
            <div className="pt-4 mt-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium w-full hover:bg-red-50 text-red-500">
                <LogOut size={18} /> Logout
              </button>
            </div>
          </div>
        </div>
      )}
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
