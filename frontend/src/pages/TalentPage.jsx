import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { listTalents } from '../api/talents';
import { Avatar } from '../components/UI';


function TalentCard({ talent, onClick }) {
  const name = talent.user?.full_name || talent.user?.email || '—';
  const skills = (talent.skills || []).slice(0, 3);
  return (
    <div onClick={onClick}
         className="bg-white rounded-2xl p-5 border cursor-pointer hover:shadow-md transition-shadow"
         style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-start gap-3 mb-3">
        <Avatar name={name} size={48} />
        <div className="min-w-0">
          <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>{name}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{talent.headline || '—'}</p>
          {(talent.city || talent.country) && (
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {[talent.city, talent.country].filter(Boolean).join(', ')}
            </p>
          )}
        </div>
      </div>
      {talent.is_available && (
        <span className="text-xs px-2.5 py-1 rounded-full font-medium"
              style={{ background: '#D1FAE5', color: '#065F46' }}>
          Open to Work
        </span>
      )}
      <div className="flex flex-wrap gap-1.5 mt-3">
        {skills.map((s) => (
          <span key={s.skill?.id || s.id} className="text-xs px-2.5 py-1 rounded-full font-medium text-white"
                style={{ background: 'var(--text-primary)' }}>
            {s.skill?.name || s.name}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function TalentPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [availableOnly, setAvailableOnly] = useState(true);

  const { data: talents, loading, error } = useApi(
    () => listTalents({
      search: query,
      is_available: availableOnly ? true : undefined,
      limit: 50,
    }),
    [query, availableOnly],
  );

  const profiles = talents || [];

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
        Talent Marketplace
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
        Browse talents on the platform.
      </p>

      <div className="flex items-center gap-3 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--text-muted)' }} />
          <input value={query} onChange={e => setQuery(e.target.value)}
                 placeholder="Search talent by name, headline, or school..."
                 className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
                 style={{ background: 'white', borderColor: 'var(--border)' }} />
        </div>
        <label className="flex items-center gap-2 text-sm whitespace-nowrap"
               style={{ color: 'var(--text-primary)' }}>
          <input type="checkbox" checked={availableOnly}
                 onChange={e => setAvailableOnly(e.target.checked)} />
          Open to work only
        </label>
      </div>

      {loading && <p className="text-sm py-10 text-center" style={{ color: 'var(--text-muted)' }}>Searching…</p>}
      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {profiles.map((t) => (
            <TalentCard key={t.id} talent={t} onClick={() => navigate(`/app/talent/${t.id}`)} />
          ))}
          {profiles.length === 0 && (
            <p className="col-span-3 text-center py-10" style={{ color: 'var(--text-muted)' }}>
              No talent found.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
