import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, SlidersHorizontal } from 'lucide-react';
import { jobs, categories } from '../data';
import { JobCardWide, Badge } from '../components/UI';

export default function JobsPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [showFilters, setShowFilters] = useState(false);
  const [filterType, setFilterType] = useState([]);
  const [filterMode, setFilterMode] = useState([]);

  const allCategories = ['All', ...categories.map(c => c.label)];
  const jobTypes = ['Full Time', 'Part Time', 'Internship', 'Contract'];
  const modes = ['Remote', 'Onsite', 'Hybrid'];

  const filtered = jobs.filter(j => {
    const matchesQuery = j.title.toLowerCase().includes(query.toLowerCase()) ||
      j.company.toLowerCase().includes(query.toLowerCase());
    const matchesCat = activeCategory === 'All' || j.category === activeCategory;
    const matchesType = filterType.length === 0 || filterType.includes(j.type);
    const matchesMode = filterMode.length === 0 || filterMode.includes(j.mode);
    return matchesQuery && matchesCat && matchesType && matchesMode;
  });

  const toggleFilter = (arr, setArr, val) =>
    setArr(a => a.includes(val) ? a.filter(x => x !== val) : [...a, val]);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>All Jobs</h1>

      {/* Search + Filter */}
      <div className="flex gap-2 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            placeholder="Search jobs..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
            style={{ background: 'white', borderColor: 'var(--border)' }}
          />
        </div>
        <button
          onClick={() => setShowFilters(s => !s)}
          className="w-12 h-12 rounded-full flex items-center justify-center border"
          style={{
            background: showFilters ? 'var(--text-primary)' : 'white',
            borderColor: 'var(--border)',
          }}
        >
          <SlidersHorizontal size={18} color={showFilters ? '#fff' : 'var(--text-secondary)'} />
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="bg-white rounded-2xl p-5 mb-6 border" style={{ borderColor: 'var(--border)' }}>
          <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>Job Type</p>
          <div className="flex flex-wrap gap-2 mb-4">
            {jobTypes.map(t => (
              <button
                key={t}
                onClick={() => toggleFilter(filterType, setFilterType, t)}
                className="px-3 py-1.5 rounded-full text-xs border"
                style={{
                  background: filterType.includes(t) ? 'var(--text-primary)' : 'transparent',
                  color: filterType.includes(t) ? '#fff' : 'var(--text-secondary)',
                  borderColor: 'var(--border)',
                }}
              >
                {t}
              </button>
            ))}
          </div>
          <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>Work Mode</p>
          <div className="flex flex-wrap gap-2">
            {modes.map(m => (
              <button
                key={m}
                onClick={() => toggleFilter(filterMode, setFilterMode, m)}
                className="px-3 py-1.5 rounded-full text-xs border"
                style={{
                  background: filterMode.includes(m) ? 'var(--text-primary)' : 'transparent',
                  color: filterMode.includes(m) ? '#fff' : 'var(--text-secondary)',
                  borderColor: 'var(--border)',
                }}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {allCategories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className="px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-all"
            style={{
              background: activeCategory === cat ? 'var(--text-primary)' : 'white',
              color: activeCategory === cat ? '#fff' : 'var(--text-primary)',
              borderColor: activeCategory === cat ? 'var(--text-primary)' : 'var(--border)',
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Results */}
      <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>{filtered.length} jobs found</p>
      <div className="flex flex-col gap-4">
        {filtered.map(job => <JobCardWide key={job.id} job={job} />)}
        {filtered.length === 0 && (
          <p className="text-center py-10" style={{ color: 'var(--text-muted)' }}>No jobs match your search.</p>
        )}
      </div>
    </div>
  );
}
