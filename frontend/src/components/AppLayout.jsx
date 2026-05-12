import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, Search, Briefcase, Users, Bell, Settings, LogOut } from 'lucide-react';
import { currentUser } from '../data';

const navItems = [
  { to: '/app/home', icon: Home, label: 'Home' },
  { to: '/app/search', icon: Search, label: 'Search' },
  { to: '/app/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/app/talent', icon: Users, label: 'Talent' },
  { to: '/app/notifications', icon: Bell, label: 'Notifications' },
  { to: '/app/settings', icon: Settings, label: 'Settings' },
];

export default function AppLayout() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* Sidebar */}
      <aside className="w-56 flex flex-col justify-between py-6 px-4 shrink-0" style={{ background: 'var(--bg)' }}>
        {/* Logo */}
        <div>
          <div className="flex items-center gap-2 px-3 mb-8">
            <LogoMark />
            <span className="font-semibold text-base" style={{ color: 'var(--text-primary)' }}>SkillBridge</span>
          </div>

          {/* Nav */}
          <nav className="flex flex-col gap-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'text-white'
                      : 'hover:bg-black/5'
                  }`
                }
                style={({ isActive }) => isActive ? { background: 'var(--text-primary)', color: '#fff' } : { color: 'var(--text-secondary)' }}
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User + Logout */}
        <div>
          <div className="flex items-center gap-2 px-3 py-2 mb-1">
            <Avatar name={currentUser.name} size={32} />
            <div className="min-w-0">
              <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>{currentUser.name}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{currentUser.role}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/sign-in')}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium w-full rounded-lg hover:bg-red-50 transition-colors"
            style={{ color: '#EF4444' }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

export function LogoMark() {
  return (
    <svg width="24" height="24" viewBox="0 0 40 40" fill="none">
      <path d="M20 8C14 8 8 12 8 18C8 22 11 25 15 26L20 32L25 26C29 25 32 22 32 18C32 12 26 8 20 8Z" fill="#1A1A1A" opacity="0.9"/>
      <path d="M14 20C14 20 17 24 20 24C23 24 26 20 26 20" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

export function Avatar({ name, size = 40, className = '' }) {
  const initials = name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?';
  return (
    <div
      className={`rounded-full flex items-center justify-center shrink-0 font-medium ${className}`}
      style={{
        width: size,
        height: size,
        background: '#D1D5DB',
        color: '#374151',
        fontSize: size * 0.35,
      }}
    >
      {initials}
    </div>
  );
}
