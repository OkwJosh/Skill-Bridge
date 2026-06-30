/**
 * SearchPage — role-aware.
 *
 *   Talent            → searches OPPORTUNITIES (internships, projects)
 *   Mentor / Org admin → searches TALENTS by name, headline, or skill
 *
 * School admins don't get a Search tab (see AppLayout), so they never
 * land here.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import { getOpportunities } from '../api/opportunities';
import { listTalents } from '../api/talents';
import { JobCardWide, Avatar, JobCardWideSkeleton, TalentResultCardSkeleton } from '../components/UI';

const TALENT_SUGGESTIONS = ['Python', 'React', 'Data Analysis', 'Figma', 'Django', 'DevOps'];
const OPPORTUNITY_SUGGESTIONS = ['Software Engineer', 'Data Analyst', 'Product Designer',
                                 'Frontend', 'Cloud', 'Internship'];

function adaptJob(op) {
  return {
    id: op.id,
    title: op.title,
    company: op.organization?.name || op.poster_name || 'SkillBridge',
    companyKey: (op.organization?.name || '').toLowerCase().replace(/\s/g, ''),
    location: op.location || (op.is_remote ? 'Remote' : 'On-site'),
    type: op.opportunity_type,
    mode: op.is_remote ? 'Remote' : 'Onsite',
    salaryMin: 0, salaryMax: 0,
    compensationLabel: op.compensation || (op.is_paid ? 'Paid' : 'Unpaid'),
    deadline: op.application_deadline
      ? new Date(op.application_deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
      : 'Open',
    saved: false,
  };
}

export default function SearchPage() {
  const { isTalent } = useAuth();
  // Anyone who isn't a talent (mentor / org admin) searches talents.
  const searchTalents = !isTalent;

  const [query, setQuery] = useState('');
  const [submitted, setSubmitted] = useState('');

  const { data: rawResults, loading } = useApi(
    () => {
      if (!submitted) return Promise.resolve([]);
      return searchTalents
        ? listTalents({ search: submitted, limit: 30 })
        : getOpportunities({ search: submitted });
    },
    [submitted, searchTalents],
  );

  const handleSearch = (q) => { setQuery(q); setSubmitted(q); };

  const placeholder = searchTalents
    ? 'Search talent by name, headline, or skill...'
    : 'Search opportunities by title or skill...';
  const suggestions = searchTalents ? TALENT_SUGGESTIONS : OPPORTUNITY_SUGGESTIONS;
  const results = rawResults || [];

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
        {searchTalents ? 'Find Talent' : 'Find Opportunities'}
      </h1>

      {/* Search bar */}
      <div className="relative mb-6">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          autoFocus
          placeholder={placeholder}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch(query)}
          className="w-full pl-11 pr-10 py-3 rounded-full text-sm border"
          style={{ background: 'white', borderColor: 'var(--border)' }}
        />
        {query && (
          <button onClick={() => { setQuery(''); setSubmitted(''); }}
                  className="absolute right-4 top-1/2 -translate-y-1/2">
            <X size={16} style={{ color: 'var(--text-muted)' }} />
          </button>
        )}
      </div>

      {/* Suggestions */}
      {!submitted && (
        <div>
          <p className="text-xs font-medium mb-3" style={{ color: 'var(--text-muted)' }}>
            {searchTalents ? 'POPULAR SKILLS' : 'POPULAR SEARCHES'}
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map(s => (
              <button key={s} onClick={() => handleSearch(s)}
                className="px-4 py-2 rounded-full text-sm border hover:bg-gray-50"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {submitted && (
        <div>
          {!loading && (
            <>
              <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
                {results.length} result{results.length !== 1 ? 's' : ''} for "<strong>{submitted}</strong>"
              </p>

              {results.length === 0 && (
                <p className="text-center py-10" style={{ color: 'var(--text-muted)' }}>
                  No results found. Try a different search.
                </p>
              )}
            </>
          )}

          {searchTalents ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => <TalentResultCardSkeleton key={i} />)
                : results.map(t => <TalentResultCard key={t.id} talent={t} />)}
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {loading
                ? Array.from({ length: 5 }).map((_, i) => <JobCardWideSkeleton key={i} />)
                : results.map(job => <JobCardWide key={job.id} job={adaptJob(job)} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TalentResultCard({ talent }) {
  const navigate = useNavigate();
  const name = talent.user?.full_name || talent.user?.email || 'Talent';
  return (
    <div onClick={() => navigate(`/app/talent/${talent.id}`)}
         className="bg-white rounded-2xl p-4 border cursor-pointer hover:shadow-md transition-shadow"
         style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-start gap-3 mb-2">
        <Avatar name={name} size={42} />
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>{name}</p>
          <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
            {talent.headline || '—'}
          </p>
        </div>
        {talent.is_available && (
          <span className="text-xs px-2 py-0.5 rounded-full font-medium shrink-0"
                style={{ background: '#D1FAE5', color: '#065F46' }}>
            Open
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-1">
        {(talent.skills || []).slice(0, 4).map(s => (
          <span key={s.skill?.id || s.id}
                className="text-xs px-2 py-0.5 rounded-full font-medium text-white"
                style={{ background: 'var(--text-primary)' }}>
            {s.skill?.name || s.name}
          </span>
        ))}
      </div>
    </div>
  );
}
