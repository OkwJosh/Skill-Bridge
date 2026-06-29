/**
 * CreateSchoolPage — first-time setup for a school_admin user.
 *
 * The backend's /schools/me/ returns 404 with code 'no_school' until the
 * caller is in `School.admins`. POSTing here creates the School AND
 * adds the caller as an admin.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { createMySchool } from '../api/schools';
import { useAuth } from '../context/AuthContext';

const SCHOOL_TYPES = [
  { value: 'university',  label: 'University'  },
  { value: 'polytechnic', label: 'Polytechnic' },
  { value: 'bootcamp',    label: 'Bootcamp'    },
  { value: 'other',       label: 'Other'       },
];

export default function CreateSchoolPage() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const [name, setName] = useState('');
  const [schoolType, setSchoolType] = useState('university');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('Nigeria');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!name.trim()) { setError('School name is required.'); return; }
    setBusy(true); setError('');
    try {
      await createMySchool({
        name: name.trim(),
        school_type: schoolType,
        website_url: websiteUrl.trim(),
        contact_email: contactEmail.trim(),
        city: city.trim(),
        state: state.trim(),
        country: country.trim(),
      });
      await refreshUser();
      navigate('/app/school', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell>
      <div className="w-full max-w-md mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center"
            style={{ fontFamily: "'DM Serif Display', serif", color: 'var(--text-primary)' }}>
          Register your<br />school
        </h1>
        <p className="text-sm text-center mb-6" style={{ color: 'var(--text-secondary)' }}>
          You'll be set as the school admin. You can upload your student roster afterwards.
        </p>

        <div className="flex flex-col gap-3 mb-4">
          <FieldRow label="School name *" value={name} onChange={setName}
                    placeholder="e.g. University of Lagos" />

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>School type</label>
            <select value={schoolType} onChange={e => setSchoolType(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg text-sm border"
                    style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}>
              {SCHOOL_TYPES.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <FieldRow label="Website" value={websiteUrl} onChange={setWebsiteUrl}
                    placeholder="https://unilag.edu.ng" type="url" />
          <FieldRow label="Contact email" value={contactEmail} onChange={setContactEmail}
                    placeholder="registrar@example.edu" type="email" />
          <FieldRow label="City" value={city} onChange={setCity} placeholder="Lagos" />
          <FieldRow label="State" value={state} onChange={setState} placeholder="Lagos" />
          <FieldRow label="Country" value={country} onChange={setCountry} />
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleSubmit} disabled={busy}>
          {busy ? 'Creating…' : 'Register school'}
        </Button>
      </div>
    </AuthShell>
  );
}

function FieldRow({ label, value, onChange, placeholder, type = 'text' }) {
  return (
    <div>
      <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)}
             placeholder={placeholder}
             className="w-full px-4 py-3 rounded-lg text-sm border"
             style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
    </div>
  );
}
