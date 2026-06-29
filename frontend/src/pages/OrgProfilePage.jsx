import { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { getMyOrganization, updateMyOrganization } from '../api/organizations';
import { uploadToSupabase } from '../api/uploads';
import { Button, PageHeader } from '../components/UI';

const SIZES = ['', '1-10', '11-50', '51-200', '201-500', '501+'];

export default function OrgProfilePage() {
  const navigate = useNavigate();
  const { data: org, loading, error, refetch } = useApi(getMyOrganization);

  // If org admin hasn't created their org yet, route to /create-organization
  // instead of showing a 404. The backend returns the literal message
  // "User is not a member of any organization." which the api client surfaces.
  useEffect(() => {
    if (error && /no_organization|not a member|does not belong/i.test(error)) {
      navigate('/create-organization', { replace: true });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error]);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('');

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [logoUploading, setLogoUploading] = useState(false);
  const [logoError, setLogoError] = useState('');
  const logoFileRef = useRef(null);

  const handleLogoPick = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLogoUploading(true); setLogoError('');
    try {
      const url = await uploadToSupabase(file, 'org_logo');
      setLogoUrl(url);
    } catch (err) {
      setLogoError(err.message);
    } finally {
      setLogoUploading(false);
      if (logoFileRef.current) logoFileRef.current.value = '';
    }
  };

  useEffect(() => {
    if (org) {
      setName(org.name || '');
      setDescription(org.description || '');
      setWebsiteUrl(org.website_url || '');
      setLogoUrl(org.logo_url || '');
      setCompanySize(org.company_size || '');
      setCity(org.city || '');
      setState(org.state || '');
      setCountry(org.country || '');
    }
  }, [org]);

  const handleSave = async () => {
    setSaving(true); setSaveError(''); setSuccess(false);
    try {
      await updateMyOrganization({
        name, description, website_url: websiteUrl, logo_url: logoUrl,
        company_size: companySize, city, state, country,
      });
      await refetch();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8"><p style={{ color: 'var(--text-muted)' }}>Loading…</p></div>;
  // The "no organization" case is handled by the redirect above; any other
  // error renders inline.
  if (error && !/no_organization|not a member|does not belong/i.test(error)) {
    return <div className="p-8"><p style={{ color: 'var(--red)' }}>{error}</p></div>;
  }
  if (!org) return null;  // brief flicker before redirect lands

  return (
    <div className="p-8 max-w-2xl">
      <PageHeader title="Organization Profile" onBack />

      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>About</p>
        <Field label="Name" value={name} onChange={setName} />
        <Field label="Description" value={description} onChange={setDescription} multiline />
        <Field label="Website" value={websiteUrl} onChange={setWebsiteUrl} type="url" />

        <div className="mb-3">
          <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>Logo</p>
          <div className="flex items-center gap-3">
            {logoUrl && (
              <img src={logoUrl} alt="logo" className="w-12 h-12 rounded-lg object-cover"
                   style={{ background: '#F3F4F6' }} />
            )}
            <input type="url" value={logoUrl || ''} onChange={e => setLogoUrl(e.target.value)}
                   placeholder="Paste a URL, or upload below"
                   className="flex-1 px-3 py-2 text-sm border rounded-lg"
                   style={{ borderColor: 'var(--border)' }} />
            <input ref={logoFileRef} type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml"
                   className="hidden" onChange={handleLogoPick} />
            <button type="button" onClick={() => logoFileRef.current?.click()} disabled={logoUploading}
                    className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium border whitespace-nowrap disabled:opacity-50"
                    style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              <Upload size={14} /> {logoUploading ? 'Uploading…' : 'Upload'}
            </button>
          </div>
          {logoError && <p className="text-xs mt-1" style={{ color: 'var(--red)' }}>{logoError}</p>}
        </div>
        <div className="mb-3">
          <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>Company size</p>
          <select value={companySize} onChange={e => setCompanySize(e.target.value)}
                  className="w-full px-3 py-2 text-sm border rounded-lg" style={{ borderColor: 'var(--border)' }}>
            {SIZES.map(s => <option key={s} value={s}>{s || 'Choose…'}</option>)}
          </select>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Location</p>
        <Field label="City" value={city} onChange={setCity} />
        <Field label="State" value={state} onChange={setState} />
        <Field label="Country" value={country} onChange={setCountry} />
      </div>

      {saveError && <p className="text-sm mt-2" style={{ color: 'var(--red)' }}>{saveError}</p>}
      {success && <p className="text-sm mt-2" style={{ color: 'var(--green)' }}>Organization updated.</p>}

      <div className="mt-4">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving…' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', multiline }) {
  return (
    <div className="mb-3">
      <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      {multiline ? (
        <textarea value={value || ''} onChange={e => onChange(e.target.value)}
                  rows={3} className="w-full px-3 py-2 text-sm border rounded-lg resize-y"
                  style={{ borderColor: 'var(--border)' }} />
      ) : (
        <input type={type} value={value || ''} onChange={e => onChange(e.target.value)}
               className="w-full px-3 py-2 text-sm border rounded-lg"
               style={{ borderColor: 'var(--border)' }} />
      )}
    </div>
  );
}
