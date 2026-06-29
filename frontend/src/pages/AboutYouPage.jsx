import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { Pencil } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { updateMe } from '../api/auth';
import { updateMyTalentProfile } from '../api/talents';

export default function AboutYouPage() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [city, setCity] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Pre-fill from anything the user already provided at signup
  useEffect(() => {
    if (user) {
      setName(user.full_name || '');
      setPhone(user.phone_number || '');
    }
  }, [user]);

  const handleContinue = async () => {
    if (!name.trim()) { setError('Please enter your name.'); return; }
    setSaving(true); setError('');
    try {
      // 1) User-level fields go on /auth/me/
      await updateMe({
        full_name: name.trim(),
        phone_number: phone.trim(),
      });
      // 2) Location lives on TalentProfile, not User.
      // Patching it auto-creates the profile if missing on the backend.
      await updateMyTalentProfile({ city: city.trim() });
      await refreshUser();
      navigate('/add-skills');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center" style={{ fontFamily: "'DM Serif Display', serif" }}>
          Tell us<br />about you
        </h1>
        <p className="text-sm text-center mb-8" style={{ color: 'var(--text-secondary)' }}>
          Help us get to know you better, it only takes a moment.
        </p>

        {/* Avatar (upload not yet wired) */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" fill="#9CA3AF"/>
                <path d="M4 20C4 16 7.58 13 12 13C16.42 13 20 16 20 20" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <button type="button" disabled className="absolute bottom-0 right-0 w-6 h-6 rounded-full flex items-center justify-center opacity-50 cursor-not-allowed"
                    style={{ background: 'var(--text-primary)' }}>
              <Pencil size={12} color="white" />
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-3 mb-5">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Your Name</label>
            <input value={name} onChange={e => setName(e.target.value)}
                   className="w-full px-4 py-3.5 rounded-full text-sm border"
                   style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Phone Number</label>
            <input value={phone} onChange={e => setPhone(e.target.value)}
                   placeholder="+234..."
                   className="w-full px-4 py-3.5 rounded-full text-sm border"
                   style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>City</label>
            <input value={city} onChange={e => setCity(e.target.value)}
                   placeholder="Lagos"
                   className="w-full px-4 py-3.5 rounded-full text-sm border"
                   style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
          </div>
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleContinue} disabled={saving}>
          {saving ? 'Saving…' : 'Continue'}
        </Button>
      </div>
    </AuthShell>
  );
}
