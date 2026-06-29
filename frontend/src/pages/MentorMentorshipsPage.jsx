import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Users, X } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { listMyMentorships, createMentorship, getMyMentorProfile } from '../api/mentors';
import { listTalents } from '../api/talents';
import { Avatar, Button } from '../components/UI';

const STATUSES = ['all', 'active', 'paused', 'ended'];

export default function MentorMentorshipsPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('active');
  const [addOpen, setAddOpen] = useState(false);
  const [selectedTalent, setSelectedTalent] = useState(null);
  const [focusArea, setFocusArea] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const { data: profile } = useApi(getMyMentorProfile);
  const { data: mentorships, loading, error: listError, refetch } = useApi(
    () => listMyMentorships(statusFilter === 'all' ? null : statusFilter),
    [statusFilter],
  );

  const handleAdd = async () => {
    if (!selectedTalent) { setError('Pick a talent first.'); return; }
    setBusy(true); setError('');
    try {
      await createMentorship({
        talent_profile_id: selectedTalent.id,
        focus_area: focusArea,
      });
      setSelectedTalent(null); setFocusArea(''); setAddOpen(false);
      await refetch();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const items = mentorships || [];
  const activeCount  = items.filter(m => m.status === 'active').length;
  const totalCount   = profile ? items.length : 0;

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>My Mentorships</h1>
      <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>
        {profile?.headline || 'Manage your mentees and sessions.'}
      </p>
      <p className="text-xs mb-6" style={{ color: 'var(--text-muted)' }}>
        Open a mentee to schedule sessions and <strong>endorse their skills</strong> —
        endorsements boost their Trust Score.
      </p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Active mentees" value={activeCount} />
        <StatCard label="Total relationships" value={totalCount} />
        <StatCard label="Endorsements given" value={profile?.endorsements_given ?? 0} />
      </div>

      {/* Add bar */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2">
          {STATUSES.map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
                    className="px-3 py-1.5 rounded-full text-xs border capitalize"
                    style={{
                      background: statusFilter === s ? 'var(--text-primary)' : 'white',
                      color: statusFilter === s ? '#fff' : 'var(--text-primary)',
                      borderColor: statusFilter === s ? 'var(--text-primary)' : 'var(--border)',
                    }}>
              {s}
            </button>
          ))}
        </div>
        <button onClick={() => setAddOpen(o => !o)}
                className="flex items-center gap-1 text-sm font-medium px-3 py-2 rounded-lg border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
          <Plus size={14} /> Add mentee
        </button>
      </div>

      {addOpen && (
        <div className="bg-white rounded-2xl p-5 border mb-5" style={{ borderColor: 'var(--border)' }}>
          <p className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>
            Add a mentee
          </p>
          <div className="flex flex-col gap-3">
            {selectedTalent ? (
              <SelectedTalentChip talent={selectedTalent} onClear={() => setSelectedTalent(null)} />
            ) : (
              <TalentPicker onPick={setSelectedTalent} />
            )}
            <input value={focusArea} onChange={e => setFocusArea(e.target.value)}
                   placeholder="Focus area (e.g. System design for backend roles)"
                   className="px-3 py-2 text-sm rounded-lg border" style={{ borderColor: 'var(--border)' }} />
            {error && <p className="text-xs" style={{ color: 'var(--red)' }}>{error}</p>}
            <div className="flex gap-2">
              <Button onClick={handleAdd} disabled={busy || !selectedTalent}>
                {busy ? 'Adding…' : 'Add mentee'}
              </Button>
              <button onClick={() => { setAddOpen(false); setSelectedTalent(null); setError(''); }}
                      className="px-4 py-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Loading…</p>}
      {listError && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{listError}</p>}

      {!loading && !listError && items.length === 0 && (
        <div className="text-center py-12">
          <Users size={32} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>No mentorships in this status.</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map(m => (
          <div key={m.id}
               onClick={() => navigate(`/app/mentor/mentorships/${m.id}`)}
               className="bg-white rounded-2xl p-5 border cursor-pointer hover:shadow-md transition-shadow"
               style={{ borderColor: 'var(--border)' }}>
            <div className="flex items-start gap-3 mb-2">
              <Avatar name={m.talent?.full_name || m.talent?.email} size={42} />
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                  {m.talent?.full_name || m.talent?.email}
                </p>
                <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                  {m.talent?.headline || '—'}
                </p>
              </div>
              <span className="text-xs px-2 py-0.5 rounded-full capitalize"
                    style={{
                      background: m.status === 'active' ? '#D1FAE5'
                                : m.status === 'paused' ? '#FEF3C7' : '#F3F4F6',
                      color:      m.status === 'active' ? '#065F46'
                                : m.status === 'paused' ? '#92400E' : '#374151',
                    }}>
                {m.status}
              </span>
            </div>
            {m.focus_area && (
              <p className="text-xs italic mt-2" style={{ color: 'var(--text-secondary)' }}>
                "{m.focus_area}"
              </p>
            )}
            <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
              Started {new Date(m.started_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-2xl p-4 border" style={{ borderColor: 'var(--border)' }}>
      <p className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>{value}</p>
    </div>
  );
}


// ── Talent picker (replaces the old raw-ID number input) ──────────────────
// Debounced typeahead over /talents/. Renders each candidate with their
// name, headline, and skill tags so the mentor isn't typing blind IDs.
function TalentPicker({ onPick }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Debounce — wait 250ms after the last keystroke before hitting the API.
  useEffect(() => {
    let cancelled = false;
    setError('');
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await listTalents({
          search: query || undefined,
          is_available: true,
          limit: 8,
        });
        if (!cancelled) setResults(data || []);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [query]);

  return (
    <div>
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2"
                style={{ color: 'var(--text-muted)' }} />
        <input value={query} onChange={e => setQuery(e.target.value)} autoFocus
               placeholder="Search talent by name, headline, or skill"
               className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border"
               style={{ borderColor: 'var(--border)' }} />
      </div>

      {loading && (
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Searching…</p>
      )}
      {error && (
        <p className="text-xs mt-2" style={{ color: 'var(--red)' }}>{error}</p>
      )}

      {!loading && !error && results.length === 0 && (
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
          {query ? 'No talents match that search.' : 'No talents available.'}
        </p>
      )}

      <div className="flex flex-col gap-1.5 mt-2 max-h-72 overflow-y-auto">
        {results.map(t => {
          const name = t.user?.full_name || t.user?.email || 'Unknown';
          return (
            <button key={t.id} type="button" onClick={() => onPick(t)}
                    className="text-left p-2.5 rounded-lg border hover:bg-gray-50 transition-colors"
                    style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-start gap-2.5">
                <Avatar name={name} size={32} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                    {name}
                  </p>
                  <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                    {t.headline || '—'}
                  </p>
                  {(t.skills || []).length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {t.skills.slice(0, 4).map(s => (
                        <span key={s.skill?.id || s.id}
                              className="text-[10px] px-1.5 py-0.5 rounded-full font-medium text-white"
                              style={{ background: 'var(--text-primary)' }}>
                          {s.skill?.name || s.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}


function SelectedTalentChip({ talent, onClear }) {
  const name = talent.user?.full_name || talent.user?.email || 'Talent';
  return (
    <div className="flex items-center gap-3 p-2.5 rounded-lg border"
         style={{ borderColor: 'var(--text-primary)', background: '#F9F9F7' }}>
      <Avatar name={name} size={32} />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>{name}</p>
        <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
          {talent.headline || '—'}
        </p>
      </div>
      <button type="button" onClick={onClear}
              className="p-1 rounded-full hover:bg-gray-100"
              title="Pick a different talent">
        <X size={14} style={{ color: 'var(--text-muted)' }} />
      </button>
    </div>
  );
}
