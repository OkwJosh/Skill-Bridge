import { useState } from 'react';
import { Search, X } from 'lucide-react';
import { jobs, categories } from '../data';
import { JobCardWide } from '../components/UI';

const recentSearches = ['Product Designer', 'Remote Engineer', 'Marketing Intern'];

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const results = jobs.filter(j =>
    j.title.toLowerCase().includes(query.toLowerCase()) ||
    j.company.toLowerCase().includes(query.toLowerCase()) ||
    j.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>Search</h1>

      {/* Search input */}
      <div className="relative mb-6">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          autoFocus
          placeholder="Job title, company, or category..."
          value={query}
          onChange={e => { setQuery(e.target.value); setSubmitted(false); }}
          onKeyDown={e => e.key === 'Enter' && setSubmitted(true)}
          className="w-full pl-11 pr-10 py-3.5 rounded-full text-sm border"
          style={{ background: 'white', borderColor: 'var(--border)' }}
        />
        {query && (
          <button onClick={() => { setQuery(''); setSubmitted(false); }} className="absolute right-4 top-1/2 -translate-y-1/2">
            <X size={14} style={{ color: 'var(--text-muted)' }} />
          </button>
        )}
      </div>

      {!query && (
        <>
          {/* Recent searches */}
          <div className="mb-6">
            <p className="text-sm font-medium mb-3" style={{ color: 'var(--text-muted)' }}>Recent Searches</p>
            <div className="flex flex-col gap-2">
              {recentSearches.map(s => (
                <button
                  key={s}
                  onClick={() => { setQuery(s); setSubmitted(true); }}
                  className="flex items-center gap-3 py-2 text-sm text-left"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  <Search size={14} style={{ color: 'var(--text-muted)' }} />
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Browse by category */}
          <div>
            <p className="text-sm font-medium mb-3" style={{ color: 'var(--text-muted)' }}>Browse by Category</p>
            <div className="flex flex-wrap gap-2">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => { setQuery(cat.label); setSubmitted(true); }}
                  className="px-4 py-2 rounded-full text-sm border hover:bg-gray-50"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {query && (
        <div>
          <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
            {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
          </p>
          <div className="flex flex-col gap-4">
            {results.map(job => <JobCardWide key={job.id} job={job} />)}
            {results.length === 0 && (
              <div className="text-center py-12">
                <p className="text-lg mb-2" style={{ color: 'var(--text-muted)' }}>No results found</p>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Try a different search term</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
