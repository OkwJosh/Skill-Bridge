import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pencil } from 'lucide-react';
import { currentUser } from '../data';
import { Button, PageHeader, Avatar } from '../components/UI';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [name, setName] = useState(currentUser.name);
  const [email, setEmail] = useState(currentUser.email);
  const [phone, setPhone] = useState('8012345678');
  const [location, setLocation] = useState(currentUser.location);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const fieldStyle = {
    borderBottom: '1px solid var(--border)',
    background: 'transparent',
    width: '100%',
    padding: '10px 0',
    fontSize: 14,
    color: 'var(--text-primary)',
    outline: 'none',
  };

  return (
    <div className="p-8 max-w-2xl">
      <PageHeader title="My Profile" onBack />

      {/* Avatar */}
      <div className="flex flex-col items-center mb-8">
        <div className="relative mb-2">
          <Avatar name={name} size={72} />
          <button
            className="absolute bottom-0 right-0 w-6 h-6 rounded-full flex items-center justify-center"
            style={{ background: 'var(--text-primary)' }}
          >
            <Pencil size={12} color="white" />
          </button>
        </div>
        <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{name}</p>
      </div>

      {/* Fields */}
      <div className="flex flex-col gap-5 mb-8">
        {[
          { label: 'Name', value: name, onChange: setName },
          { label: 'Email', value: email, onChange: setEmail, type: 'email' },
          { label: 'Location', value: location, onChange: setLocation },
        ].map(({ label, value, onChange, type = 'text' }) => (
          <div key={label}>
            <label className="block text-xs mb-1" style={{ color: 'var(--text-muted)' }}>{label}</label>
            <input
              type={type}
              value={value}
              onChange={e => onChange(e.target.value)}
              style={fieldStyle}
            />
          </div>
        ))}

        {/* Phone with flag */}
        <div>
          <label className="block text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Phone Number</label>
          <div className="flex items-center gap-2" style={{ borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>
            <span>🇳🇬</span>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>+234</span>
            <input
              value={phone}
              onChange={e => setPhone(e.target.value)}
              style={{ ...fieldStyle, borderBottom: 'none', padding: 0, flex: 1 }}
            />
          </div>
        </div>
      </div>

      <Button onClick={handleSave}>
        {saved ? 'Saved ✓' : 'Save Changes'}
      </Button>
    </div>
  );
}
