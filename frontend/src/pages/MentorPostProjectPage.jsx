/**
 * MentorPostProjectPage — lets a mentor publish a guided project.
 *
 * Backend POST /opportunities/ auto-attaches the calling mentor (no
 * organization is needed) when the user has `is_mentor=True`. We force
 * opportunity_type='guided_project' here; mentors don't post jobs.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { getSkills } from '../api/core';
import { createOpportunity } from '../api/opportunities';
import { Button, PageHeader } from '../components/UI';

export default function MentorPostProjectPage() {
  const navigate = useNavigate();
  const { data: skills } = useApi(getSkills);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('');
  const [isRemote, setIsRemote] = useState(true);
  const [location, setLocation] = useState('');
  const [isPaid, setIsPaid] = useState(false);
  const [compensation, setCompensation] = useState('');
  const [maxApplicants, setMaxApplicants] = useState('');
  const [spotsAvailable, setSpotsAvailable] = useState('1');
  const [applicationDeadline, setApplicationDeadline] = useState('');
  const [startDate, setStartDate] = useState('');
  const [selectedSkillIds, setSelectedSkillIds] = useState(new Set());

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const toggleSkill = (id) => {
    setSelectedSkillIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleSubmit = async () => {
    if (!title.trim())       { setError('Title is required.');       return; }
    if (!description.trim()) { setError('Description is required.'); return; }
    setBusy(true); setError('');
    try {
      const created = await createOpportunity({
        title: title.trim(),
        description: description.trim(),
        opportunity_type: 'guided_project',
        required_skill_ids: [...selectedSkillIds],
        is_remote: isRemote,
        location: location.trim(),
        is_paid: isPaid,
        compensation: compensation.trim(),
        duration: duration.trim(),
        max_applicants: maxApplicants ? parseInt(maxApplicants, 10) : null,
        spots_available: parseInt(spotsAvailable, 10) || 1,
        application_deadline: applicationDeadline || null,
        start_date: startDate || null,
      });
      navigate(`/app/jobs/${created.id}`, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl">
      <PageHeader title="Post a guided project" onBack />

      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>About the project</p>
        <Field label="Title *" value={title} onChange={setTitle}
               placeholder="e.g. Build a CRUD API in 4 weekends" />
        <Field label="Description *" value={description} onChange={setDescription} multiline
               placeholder="What will the mentee build, learn, ship?" />
        <Field label="Duration" value={duration} onChange={setDuration}
               placeholder="e.g. 4 weeks, 8 sessions" />
      </div>

      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Required skills</p>
        <div className="flex flex-wrap gap-2 max-h-56 overflow-y-auto">
          {(skills || []).map(s => {
            const active = selectedSkillIds.has(s.id);
            return (
              <button key={s.id} type="button" onClick={() => toggleSkill(s.id)}
                      className="px-3 py-1 rounded-full text-xs font-medium border transition-all"
                      style={{
                        background: active ? 'var(--text-primary)' : 'transparent',
                        color:      active ? '#fff' : 'var(--text-primary)',
                        borderColor: active ? 'var(--text-primary)' : 'var(--border)',
                      }}>
                {s.name}
              </button>
            );
          })}
          {(skills || []).length === 0 && (
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              No skills available yet. Seed them via Django admin.
            </p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-2xl p-5 border mb-4" style={{ borderColor: 'var(--border)' }}>
        <p className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Logistics</p>
        <CheckboxRow checked={isRemote} onChange={setIsRemote} label="Remote" />
        {!isRemote && (
          <Field label="Location" value={location} onChange={setLocation}
                 placeholder="e.g. Lagos, Nigeria" />
        )}
        <CheckboxRow checked={isPaid} onChange={setIsPaid} label="Paid project" />
        {isPaid && (
          <Field label="Compensation" value={compensation} onChange={setCompensation}
                 placeholder="e.g. ₦100,000 stipend on completion" />
        )}
        <Field label="Max applicants" value={maxApplicants} onChange={setMaxApplicants}
               placeholder="Leave blank for unlimited" type="number" />
        <Field label="Spots available" value={spotsAvailable} onChange={setSpotsAvailable}
               type="number" />
        <Field label="Application deadline" value={applicationDeadline}
               onChange={setApplicationDeadline} type="datetime-local" />
        <Field label="Start date" value={startDate} onChange={setStartDate} type="date" />
      </div>

      {error && <p className="text-sm mt-2" style={{ color: 'var(--red)' }}>{error}</p>}

      <div className="mt-4">
        <Button onClick={handleSubmit} disabled={busy}>
          {busy ? 'Publishing…' : 'Publish project'}
        </Button>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, placeholder, type = 'text', multiline }) {
  return (
    <div className="mb-3">
      <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
      {multiline ? (
        <textarea value={value || ''} onChange={e => onChange(e.target.value)}
                  rows={4} placeholder={placeholder}
                  className="w-full px-3 py-2 text-sm border rounded-lg resize-y"
                  style={{ borderColor: 'var(--border)' }} />
      ) : (
        <input type={type} value={value || ''} onChange={e => onChange(e.target.value)}
               placeholder={placeholder}
               className="w-full px-3 py-2 text-sm border rounded-lg"
               style={{ borderColor: 'var(--border)' }} />
      )}
    </div>
  );
}

function CheckboxRow({ checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 mb-3 text-sm cursor-pointer"
           style={{ color: 'var(--text-primary)' }}>
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
      {label}
    </label>
  );
}
