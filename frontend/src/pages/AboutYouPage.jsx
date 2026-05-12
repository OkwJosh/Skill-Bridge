import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { Pencil } from 'lucide-react';

export default function AboutYouPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center" style={{ fontFamily: "'DM Serif Display', serif" }}>
          Tell us<br />about you
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          Help us get to know you better, it only takes a moment.
        </p>

        {/* Avatar */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#9CA3AF"/><path d="M4 20C4 16 7.58 13 12 13C16.42 13 20 16 20 20" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/></svg>
            </div>
            <button className="absolute bottom-0 right-0 w-6 h-6 rounded-full flex items-center justify-center" style={{ background: 'var(--text-primary)' }}>
              <Pencil size={12} color="white" />
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-3 mb-5">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Your Name</label>
            <input
              placeholder="Goodnews Enang"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full px-4 py-3.5 rounded-full text-sm border"
              style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
            />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Phone Number</label>
            <div className="flex gap-2">
              <button className="flex items-center gap-1 px-3 py-3.5 rounded-full border text-sm" style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}>
                🇳🇬 <span style={{ color: 'var(--text-muted)' }}>▾</span>
              </button>
              <input
                placeholder="+234"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                className="flex-1 px-4 py-3.5 rounded-full text-sm border"
                style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Location</label>
            <input
              placeholder="Lagos, Nigeria"
              value={location}
              onChange={e => setLocation(e.target.value)}
              className="w-full px-4 py-3.5 rounded-full text-sm border"
              style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
            />
          </div>
        </div>

        <Button onClick={() => navigate('/add-skills')}>Continue</Button>
      </div>
    </AuthShell>
  );
}
