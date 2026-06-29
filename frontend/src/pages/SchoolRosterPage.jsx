import { useRef, useState } from 'react';
import { Plus, Search, Upload } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { listRoster, addRosterRecord, importRosterCSV } from '../api/schools';
import { Button, PageHeader } from '../components/UI';

export default function SchoolRosterPage() {
  const [query, setQuery] = useState('');
  const [consentFilter, setConsentFilter] = useState('all');
  const [adding, setAdding] = useState(false);
  const [importSummary, setImportSummary] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState('');
  const fileRef = useRef(null);

  const params = {
    ...(query ? { search: query } : {}),
    ...(consentFilter === 'consented' ? { has_consented: true } : {}),
    ...(consentFilter === 'pending' ? { has_consented: false } : {}),
  };

  const { data: roster, loading, error, refetch } = useApi(
    () => listRoster(params), [query, consentFilter],
  );

  const handleCSVChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true); setImportError(''); setImportSummary(null);
    try {
      const summary = await importRosterCSV(file, 'skip');
      setImportSummary(summary);
      refetch();
    } catch (err) {
      setImportError(err.message);
    } finally {
      setImporting(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <div className="p-8 max-w-4xl">
      <PageHeader title="Student Roster" onBack />

      <div className="flex justify-between items-center gap-3 mb-4 flex-wrap">
        <div className="flex-1 relative min-w-60">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input value={query} onChange={e => setQuery(e.target.value)}
                 placeholder="Search by matric number, name, or email"
                 className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
                 style={{ background: 'white', borderColor: 'var(--border)' }} />
        </div>
        <input ref={fileRef} type="file" accept=".csv,text/csv" className="hidden"
               onChange={handleCSVChange} />
        <button onClick={() => fileRef.current?.click()} disabled={importing}
                className="flex items-center gap-1 text-sm font-medium px-3 py-2 rounded-lg border whitespace-nowrap disabled:opacity-50"
                style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
          <Upload size={14} /> {importing ? 'Importing…' : 'Import CSV'}
        </button>
        <button onClick={() => setAdding(o => !o)}
                className="flex items-center gap-1 text-sm font-medium px-3 py-2 rounded-lg border whitespace-nowrap"
                style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
          <Plus size={14} /> {adding ? 'Cancel' : 'Add student'}
        </button>
      </div>

      {(importSummary || importError) && (
        <div className="bg-white rounded-2xl p-4 border mb-4 text-sm"
             style={{ borderColor: 'var(--border)' }}>
          {importError && <p style={{ color: 'var(--red)' }}>{importError}</p>}
          {importSummary && (
            <>
              <p className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                Import complete · created {importSummary.created}
                {importSummary.updated ? ` · updated ${importSummary.updated}` : ''}
                {importSummary.skipped ? ` · skipped ${importSummary.skipped}` : ''}
              </p>
              {importSummary.errors?.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs" style={{ color: 'var(--text-muted)' }}>
                    {importSummary.errors.length} row error{importSummary.errors.length === 1 ? '' : 's'}
                  </summary>
                  <ul className="mt-1 list-disc pl-5 text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {importSummary.errors.slice(0, 20).map((e, i) => (
                      <li key={i}>Row {e.row}: {e.message}</li>
                    ))}
                    {importSummary.errors.length > 20 && (
                      <li>… {importSummary.errors.length - 20} more</li>
                    )}
                  </ul>
                </details>
              )}
              <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
                CSV must include <code>matriculation_number</code>. Optional columns:
                email, full_name, department, course_of_study, enrollment_year,
                expected_graduation_year, graduation_year, is_graduated, cgpa.
              </p>
            </>
          )}
        </div>
      )}

      <div className="flex gap-2 mb-4">
        {['all', 'consented', 'pending'].map(f => (
          <button key={f} onClick={() => setConsentFilter(f)}
                  className="px-3 py-1 rounded-full text-xs border capitalize"
                  style={{
                    background: consentFilter === f ? 'var(--text-primary)' : 'white',
                    color: consentFilter === f ? '#fff' : 'var(--text-primary)',
                    borderColor: consentFilter === f ? 'var(--text-primary)' : 'var(--border)',
                  }}>
            {f}
          </button>
        ))}
      </div>

      {adding && <AddForm onCreated={() => { setAdding(false); refetch(); }} />}

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && (roster || []).length === 0 && (
        <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>
          No roster records yet.
        </p>
      )}

      <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
        {(roster || []).map((r, i) => (
          <div key={r.id}
               className="px-4 py-3 flex items-center justify-between"
               style={{ borderBottom: i < (roster || []).length - 1 ? '1px solid var(--border)' : 'none' }}>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                {r.full_name || '—'} <span className="text-xs font-normal" style={{ color: 'var(--text-muted)' }}>
                  · {r.matriculation_number}
                </span>
              </p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {r.email}{r.department && ` · ${r.department}`}
                {r.course_of_study && ` · ${r.course_of_study}`}
              </p>
            </div>
            {r.has_consented ? (
              <span className="text-xs px-2 py-0.5 rounded-full"
                    style={{ background: '#D1FAE5', color: '#065F46' }}>
                Consented
              </span>
            ) : (
              <span className="text-xs px-2 py-0.5 rounded-full"
                    style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
                Pending
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}


function AddForm({ onCreated }) {
  const [matriculationNumber, setMatricNo] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [department, setDepartment] = useState('');
  const [courseOfStudy, setCourseOfStudy] = useState('');
  const [enrollmentYear, setEnrollmentYear] = useState('');
  const [expectedGraduationYear, setExpectedGraduationYear] = useState('');
  const [cgpa, setCgpa] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const handle = async () => {
    if (!matriculationNumber.trim()) { setError('Matriculation number is required.'); return; }
    setBusy(true); setError('');
    try {
      await addRosterRecord({
        matriculation_number: matriculationNumber.trim(),
        email: email.trim(),
        full_name: fullName.trim(),
        department: department.trim(),
        course_of_study: courseOfStudy.trim(),
        enrollment_year: enrollmentYear ? parseInt(enrollmentYear, 10) : null,
        expected_graduation_year: expectedGraduationYear ? parseInt(expectedGraduationYear, 10) : null,
        cgpa: cgpa ? parseFloat(cgpa) : null,
      });
      onCreated();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="bg-white rounded-2xl p-5 border mb-5" style={{ borderColor: 'var(--border)' }}>
      <p className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Add student to roster</p>
      <div className="grid grid-cols-2 gap-2">
        <Input label="Matric number*" value={matriculationNumber} onChange={setMatricNo} />
        <Input label="Email" value={email} onChange={setEmail} type="email" />
        <Input label="Full name" value={fullName} onChange={setFullName} />
        <Input label="Department" value={department} onChange={setDepartment} />
        <Input label="Course" value={courseOfStudy} onChange={setCourseOfStudy} />
        <Input label="CGPA" value={cgpa} onChange={setCgpa} type="number" step="0.01" />
        <Input label="Enrolled year" value={enrollmentYear} onChange={setEnrollmentYear} type="number" />
        <Input label="Expected grad year" value={expectedGraduationYear} onChange={setExpectedGraduationYear} type="number" />
      </div>
      {error && <p className="text-xs mt-2" style={{ color: 'var(--red)' }}>{error}</p>}
      <Button onClick={handle} disabled={busy} className="mt-3">
        {busy ? 'Adding…' : 'Add to roster'}
      </Button>
    </div>
  );
}

function Input({ label, value, onChange, type = 'text', step }) {
  return (
    <div>
      <label className="block text-xs mb-1" style={{ color: 'var(--text-muted)' }}>{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)} step={step}
             className="w-full px-3 py-2 text-sm border rounded-lg"
             style={{ borderColor: 'var(--border)' }} />
    </div>
  );
}
