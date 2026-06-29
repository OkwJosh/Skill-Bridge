import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { Search, Plus } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { getSkills, createSkill } from '../api/core';
import { addSkill } from '../api/talents';

const PROFICIENCY = [
  { value: 'beginner',     label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced',     label: 'Advanced' },
  { value: 'expert',       label: 'Expert' },
];

export default function AddSkillsPage() {
  const navigate = useNavigate();
  const { data: allSkills, loading: skillsLoading, error: skillsError, refetch: refetchSkills } = useApi(getSkills);

  const [selectedIds, setSelectedIds] = useState(new Set());
  const [proficiency, setProficiency] = useState('intermediate');
  const [query, setQuery] = useState('');
  const [creatingSkill, setCreatingSkill] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const toggle = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  // Group skills by category for a cleaner picker
  const groups = useMemo(() => {
    const filtered = (allSkills || []).filter(
      s => !query || s.name.toLowerCase().includes(query.toLowerCase())
    );
    return filtered.reduce((acc, s) => {
      const cat = s.category || 'Other';
      (acc[cat] ||= []).push(s);
      return acc;
    }, {});
  }, [allSkills, query]);

  // True when the user's search text has no exact match → offer to create.
  const exactMatch = useMemo(
    () => (allSkills || []).some(s => s.name.toLowerCase() === query.trim().toLowerCase()),
    [allSkills, query],
  );
  const canCreate = query.trim().length > 0 && !exactMatch;

  const handleCreateAndSelect = async () => {
    setCreatingSkill(true); setError('');
    try {
      const created = await createSkill(query.trim());
      await refetchSkills();
      setSelectedIds(prev => new Set(prev).add(created.id));
      setQuery('');
    } catch (err) {
      setError(err.message);
    } finally {
      setCreatingSkill(false);
    }
  };

  const handleContinue = async () => {
    if (selectedIds.size === 0) {
      setError('Pick at least one skill, or skip for now.');
      return;
    }
    setSaving(true); setError('');
    try {
      // POST each skill in sequence (small N — no batching needed).
      // Backend de-dupes via unique_together(talent, skill).
      for (const id of selectedIds) {
        try {
          await addSkill({ skill_id: id, proficiency, years_experience: 0, is_primary: false });
        } catch (err) {
          // Tolerate already-added skills; surface anything else.
          if (!/already/i.test(err.message)) throw err;
        }
      }
      navigate('/account-success');
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
          Add your<br />skills
        </h1>
        <p className="text-sm text-center mb-6" style={{ color: 'var(--text-secondary)' }}>
          Pick what you know. You can always change these later.
        </p>

        {/* Search */}
        <div className="relative mb-2">
          <Search size={14} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            placeholder="Search or type a new skill (e.g., Python, Figma)"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && canCreate && handleCreateAndSelect()}
            className="w-full pl-10 pr-4 py-3 rounded-full text-sm border"
            style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
          />
        </div>

        {/* "Add this skill" affordance when no exact match */}
        {canCreate && (
          <button onClick={handleCreateAndSelect} disabled={creatingSkill}
                  className="mb-3 flex items-center gap-1 text-xs font-medium underline"
                  style={{ color: 'var(--text-primary)' }}>
            <Plus size={12} />
            {creatingSkill ? 'Adding…' : `Add "${query.trim()}" as a new skill`}
          </button>
        )}

        {skillsLoading && (
          <p className="text-sm py-8 text-center" style={{ color: 'var(--text-muted)' }}>Loading skills…</p>
        )}
        {skillsError && (
          <p className="text-sm py-4 text-center" style={{ color: 'var(--red)' }}>{skillsError}</p>
        )}
        {!skillsLoading && !skillsError && Object.keys(groups).length === 0 && (
          <p className="text-sm py-8 text-center" style={{ color: 'var(--text-muted)' }}>
            No skills available yet. Ask your admin to run <code>seed_data</code>.
          </p>
        )}

        {/* Skill chips by category */}
        <div className="mb-6 max-h-72 overflow-y-auto">
          {Object.entries(groups).map(([cat, items]) => (
            <div key={cat} className="mb-4">
              <p className="text-xs font-semibold mb-2 uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                {cat}
              </p>
              <div className="flex flex-wrap gap-2">
                {items.map(skill => {
                  const active = selectedIds.has(skill.id);
                  return (
                    <button key={skill.id} type="button" onClick={() => toggle(skill.id)}
                            className="px-3 py-1.5 rounded-full text-xs font-medium border transition-all"
                            style={{
                              background: active ? 'var(--text-primary)' : 'transparent',
                              color: active ? '#fff' : 'var(--text-primary)',
                              borderColor: active ? 'var(--text-primary)' : 'var(--border)',
                            }}>
                      {skill.name}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Proficiency for the batch */}
        <div className="mb-6">
          <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
            Proficiency (applies to all selected)
          </p>
          <div className="flex flex-col gap-2">
            {PROFICIENCY.map(p => (
              <label key={p.value} className="flex items-center gap-3 cursor-pointer">
                <div onClick={() => setProficiency(p.value)}
                     className="w-5 h-5 rounded-full border-2 flex items-center justify-center cursor-pointer"
                     style={{ borderColor: proficiency === p.value ? 'var(--text-primary)' : 'var(--border)' }}>
                  {proficiency === p.value && (
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: 'var(--text-primary)' }} />
                  )}
                </div>
                <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{p.label}</span>
              </label>
            ))}
          </div>
        </div>

        {error && <p className="text-xs mb-3 px-1" style={{ color: 'var(--red)' }}>{error}</p>}

        <Button onClick={handleContinue} disabled={saving} className="mb-2">
          {saving ? 'Saving…' : `Add ${selectedIds.size} skill${selectedIds.size === 1 ? '' : 's'}`}
        </Button>
        <Button variant="ghost" onClick={() => navigate('/account-success')}>Skip for now</Button>
      </div>
    </AuthShell>
  );
}
