import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { talentProfiles } from '../data';
import { Avatar, Badge } from '../components/UI';

export default function TalentPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  const filtered = talentProfiles.filter(t =>
    t.name.toLowerCase().includes(query.toLowerCase()) ||
    t.role.toLowerCase().includes(query.toLowerCase()) ||
    t.skills.some(s => s.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>Talent Marketplace</h1>

      {/* Search */}
      <div className="relative mb-6">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          placeholder="Search by name, role, or skill..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
          style={{ background: 'white', borderColor: 'var(--border)' }}
        />
      </div>

      <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>{filtered.length} talents found</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(talent => (
          <div
            key={talent.id}
            onClick={() => navigate(`/app/talent/${talent.id}`)}
            className="bg-white rounded-2xl p-5 cursor-pointer hover:shadow-md transition-shadow border"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="flex items-start gap-3 mb-3">
              <Avatar name={talent.name} size={48} />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{talent.name}</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{talent.role}</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>📍 {talent.location}</p>
              </div>
              <span className="text-xs px-2 py-1 rounded-full font-medium shrink-0" style={{ background: '#D1FAE5', color: '#065F46' }}>
                {talent.status}
              </span>
            </div>
            <p className="text-xs leading-relaxed mb-3 line-clamp-2" style={{ color: 'var(--text-secondary)' }}>
              {talent.about}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {talent.skills.map(skill => (
                <span
                  key={skill}
                  className="text-xs px-3 py-1 rounded-full font-medium"
                  style={{ background: 'var(--text-primary)', color: '#fff' }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
