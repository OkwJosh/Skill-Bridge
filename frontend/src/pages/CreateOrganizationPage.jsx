/**
 * CreateOrganizationPage — first-time setup for an org_admin user.
 *
 * Required after signup when role=org_admin, because the backend's
 * /organizations/me/ returns 404 with code 'no_organization' until the
 * caller belongs to an `OrganizationMember` row. Posting here creates
 * the Organization AND adds the caller as owner.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { useApi } from '../hooks/useApi';
import { createMyOrganization } from '../api/organizations';
import { getIndustries } from '../api/core';
import { useAuth } from '../context/AuthContext';

const SIZES = ['', '1-10', '11-50', '51-200', '201-500', '501+'];

export default function CreateOrganizationPage() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const { data: industries } = useApi(getIndustries);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [industryId, setIndustryId] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('Nigeria');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!name.trim()) { setError('Organization name is required.'); return; }
    setBusy(true); setError('');
    try {
      await createMyOrganization({
        name: name.trim(),
        description: description.trim(),
        website_url: websiteUrl.trim(),
        industry_id: industryId ? parseInt(industryId, 10) : null,
        company_size: companySize,
        city: city.trim(),
        country: country.trim(),
      });
      await refreshUser();
      navigate('/app/org/profile', { replace: true });
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
          Set up your<br />organization
        </h1>
        <p className="text-sm text-center mb-6" style={{ color: 'var(--text-secondary)' }}>
          You'll be the owner. You can invite teammates later.
        </p>

        <div className="flex flex-col gap-3 mb-4">
          <FieldRow label="Organization name *" value={name} onChange={setName} placeholder="Acme Tech" />
          <FieldRow label="Description" value={description} onChange={setDescription} multiline
                    placeholder="What does your organization do?" />
          <FieldRow label="Website" value={websiteUrl} onChange={setWebsiteUrl}
                    placeholder="https://acmetech.com" type="url" />

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Industry</label>
            <select value={industryId} onChange={e => setIndustryId(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg text-sm border"
                    style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}>
              <option value="">Choose…</option>
              {(industries || []).map(i => (
                <option key={i.id} value={i.id}>{i.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Company size</label>
            <select value={companySize} onChange={e => setCompanySize(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg text-sm border"
                    style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}>
              {SIZES.map(s => <option key={s} value={s}>{s || 'Choose…'}</option>)}
            </select>
          </div>

          <FieldRow label="City" value={city} onChange={setCity} placeholder="Lagos" />
          <FieldRow label="Country" value={country} onChange={setCountry} />
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleSubmit} disabled={busy}>
          {busy ? 'Creating…' : 'Create organization'}
        </Button>
      </div>
    </AuthShell>
  );
}

function FieldRow({ label, value, onChange, placeholder, type = 'text', multiline }) {
  return (
    <div>
      <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>{label}</label>
      {multiline ? (
        <textarea value={value} onChange={e => onChange(e.target.value)} rows={2}
                  placeholder={placeholder}
                  className="w-full px-4 py-3 rounded-lg text-sm border resize-y"
                  style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
      ) : (
        <input type={type} value={value} onChange={e => onChange(e.target.value)}
               placeholder={placeholder}
               className="w-full px-4 py-3 rounded-lg text-sm border"
               style={{ background: '#F9F9F7', borderColor: 'var(--border)' }} />
      )}
    </div>
  );
}
