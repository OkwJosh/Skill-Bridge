import { Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { formatSalary } from '../data';
import { useState } from 'react';

// ─── Company Logo ─────────────────────────────────────────────────
const logoColors = {
  google: '#4285F4', slack: '#4A154B', microsoft: '#00A4EF',
  spotify: '#1DB954', netflix: '#E50914', airbnb: '#FF5A5F',
  adobe: '#FF0000', meta: '#0866FF',
};

export function CompanyLogo({ companyKey, size = 40 }) {
  const color = logoColors[companyKey] || '#6B7280';
  const letter = companyKey?.[0]?.toUpperCase() || '?';
  return (
    <div
      className="rounded-xl flex items-center justify-center font-bold text-white shrink-0"
      style={{ width: size, height: size, background: color, fontSize: size * 0.4 }}
    >
      {letter}
    </div>
  );
}

export function Avatar({ src, alt = "avatar", name = "", size = 48 }) {
  const initials = name
    ? name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "?";

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        overflow: "hidden",
        backgroundColor: "#ddd",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: "bold",
        color: "#555",
      }}
    >
      {src ? (
        <img
          src={src}
          alt={alt}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : (
        initials
      )}
    </div>
  );
}

// ─── Job Card (small, for grid) ───────────────────────────────────
export function JobCardSmall({ job }) {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(job.saved);
  return (
    <div
      onClick={() => navigate(`/app/jobs/${job.id}`)}
      className="bg-white rounded-2xl p-4 cursor-pointer hover:shadow-md transition-shadow border"
      style={{ borderColor: 'var(--border)' }}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <CompanyLogo companyKey={job.companyKey} size={36} />
          <div>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{job.company}</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>📍 {job.location}</p>
          </div>
        </div>
        <button
          onClick={e => { e.stopPropagation(); setSaved(s => !s); }}
          className="p-1 rounded-full hover:bg-gray-100"
        >
          <Heart size={16} fill={saved ? '#EF4444' : 'none'} color={saved ? '#EF4444' : '#9CA3AF'} />
        </button>
      </div>
      <p className="font-semibold text-sm mb-1" style={{ color: 'var(--text-primary)' }}>{job.title}</p>
      <p className="text-xs mb-3" style={{ color: 'var(--text-muted)' }}>{job.type} · {job.mode}</p>
      <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{formatSalary(job.salaryMin, job.salaryMax)}</p>
    </div>
  );
}

// ─── Job Card (wide, for list) ────────────────────────────────────
export function JobCardWide({ job }) {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(job.saved);
  return (
    <div
      onClick={() => navigate(`/app/jobs/${job.id}`)}
      className="bg-white rounded-2xl p-4 cursor-pointer hover:shadow-md transition-shadow border"
      style={{ borderColor: 'var(--border)' }}
    >
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-3">
          <CompanyLogo companyKey={job.companyKey} size={44} />
          <div>
            <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{job.title}</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{job.company}</p>
          </div>
        </div>
        <button
          onClick={e => { e.stopPropagation(); setSaved(s => !s); }}
          className="p-1.5 rounded-full hover:bg-gray-100"
        >
          <Heart size={16} fill={saved ? '#EF4444' : 'none'} color={saved ? '#EF4444' : '#9CA3AF'} />
        </button>
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        <Badge>{job.type}</Badge>
        <Badge>{job.mode}</Badge>
        <Badge>{job.location}</Badge>
      </div>
      <div className="flex justify-between items-center mt-3">
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Deadline: {job.deadline}</p>
        <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{formatSalary(job.salaryMin, job.salaryMax)}</p>
      </div>
    </div>
  );
}

// ─── Badge ────────────────────────────────────────────────────────
export function Badge({ children, active = false }) {
  return (
    <span
      className="text-xs px-3 py-1 rounded-full font-medium"
      style={{
        background: active ? 'var(--text-primary)' : '#F3F4F6',
        color: active ? '#fff' : 'var(--text-secondary)',
      }}
    >
      {children}
    </span>
  );
}

// ─── Button ──────────────────────────────────────────────────────
export function Button({ children, onClick, variant = 'primary', className = '', type = 'button', disabled = false }) {
  const base = "w-full py-3.5 rounded-full font-semibold text-sm transition-all";
  const styles = {
    primary: { background: 'var(--text-primary)', color: '#fff' },
    secondary: { background: 'transparent', color: 'var(--text-primary)', border: '1.5px solid var(--border)' },
    ghost: { background: 'transparent', color: 'var(--text-muted)' },
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90 active:scale-[0.98]'}`}
      style={styles[variant]}
    >
      {children}
    </button>
  );
}

// ─── Input ────────────────────────────────────────────────────────
export function Input({ label, placeholder, type = 'text', value, onChange, rightIcon }) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-primary)' }}>{label}</label>}
      <div className="relative">
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="w-full px-4 py-3.5 rounded-full text-sm border"
          style={{
            background: '#F9F9F7',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
          }}
        />
        {rightIcon && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }}>
            {rightIcon}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Section Header ───────────────────────────────────────────────
export function SectionHeader({ title, onSeeAll }) {
  return (
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h2>
      {onSeeAll && (
        <button onClick={onSeeAll} className="text-sm" style={{ color: 'var(--text-muted)' }}>See All</button>
      )}
    </div>
  );
}

// ─── Auth Shell (split layout) ────────────────────────────────────
export function AuthShell({ children, imageSide = true }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-6" style={{ background: '#E8E6E0' }}>
      <div className="w-full max-w-4xl rounded-3xl overflow-hidden flex shadow-2xl" style={{ minHeight: 580 }}>
        {/* Left image panel */}
        {imageSide && (
          <div
            className="hidden md:block w-1/2 relative"
            style={{
              background: 'linear-gradient(135deg, #9CA3AF 0%, #6B7280 100%)',
            }}
          >
            <div className="absolute inset-0 flex items-end p-8">
              <p className="text-white text-2xl font-light opacity-80 leading-snug">
                "Your next<br/>opportunity<br/>is here."
              </p>
            </div>
          </div>
        )}
        {/* Right form panel */}
        <div className="flex-1 bg-white flex flex-col p-10 justify-center">
          <div className="flex items-center gap-2 mb-8">
            <LogoMarkSmall />
            <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>SkillBridge</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

function LogoMarkSmall() {
  return (
    <svg width="20" height="20" viewBox="0 0 40 40" fill="none">
      <path d="M20 8C14 8 8 12 8 18C8 22 11 25 15 26L20 32L25 26C29 25 32 22 32 18C32 12 26 8 20 8Z" fill="#1A1A1A"/>
    </svg>
  );
}

// ─── Page Header (with back button) ──────────────────────────────
export function PageHeader({ title, onBack, rightSlot }) {
  const navigate = useNavigate();
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-3">
        {onBack && (
          <button
            onClick={() => navigate(-1)}
            className="w-9 h-9 rounded-full border flex items-center justify-center hover:bg-gray-50"
            style={{ borderColor: 'var(--border)' }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
        <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h1>
      </div>
      {rightSlot}
    </div>
  );
}
