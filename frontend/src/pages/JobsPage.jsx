import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, SlidersHorizontal } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { getOpportunities } from '../api/opportunities';
import { JobCardWide, JobCardWideSkeleton } from '../components/UI';
import { categories as staticCategories } from '../data';

const opportunityTypes = ['internship', 'micro_project', 'guided_project'];
const typeLabels = { internship: 'Internship', micro_project: 'Micro Project', guided_project: 'Guided Project' };
const categoryTabs = [{ id: 'All', label: 'All Categories' }, ...staticCategories];

function adaptJob(op) {
  return {
    id: op.id,
    title: op.title,
    company: op.organization?.name || 'SkillBridge',
    companyKey: (op.organization?.name || '').toLowerCase().replace(/\s/g, ''),
    location: op.location || (op.is_remote ? 'Remote' : 'On-site'),
    type: typeLabels[op.opportunity_type] || op.opportunity_type,
    mode: op.is_remote ? 'Remote' : 'Onsite',
    salaryMin: 0, salaryMax: 0,
    compensationLabel: op.compensation || (op.is_paid ? 'Paid' : 'Unpaid'),
    deadline: op.application_deadline
      ? new Date(op.application_deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
      : 'Open',
    saved: false,
  };
}

export default function JobsPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [showFilters, setShowFilters] = useState(false);
  const [filterType, setFilterType] = useState([]);

  // Build params for the API
  const params = {
    ...(query ? { search: query } : {}),
    ...(filterType.length === 1 ? { opportunity_type: filterType[0] } : {}),
    ...(activeFilter === 'Remote' ? { is_remote: true } : {}),
    ...(activeFilter === 'Paid' ? { is_paid: true } : {}),
    ...(activeFilter === 'Internship' ? { opportunity_type: 'internship' } : {}),
    ...(activeFilter === 'Micro Project' ? { opportunity_type: 'micro_project' } : {}),
    ...(activeFilter === 'Guided Project' ? { opportunity_type: 'guided_project' } : {}),
  };

  const { data: rawJobs, loading, error } = useApi(() => getOpportunities(params), [query, activeFilter, filterType.join(',')]);
  const jobs = (rawJobs || []).map(adaptJob);
  const displayJobs = activeFilter === 'All' ? jobs : jobs.filter(j => j.category === activeFilter);

  const toggleType = (t) => setFilterType(f => f.includes(t) ? f.filter(x => x !== t) : [...f, t]);

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-primary)' }}>All Opportunities</h1>

      {/* Search + Filter toggle */}
      <div className="flex gap-2 mb-4">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            placeholder="Search opportunities..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
            style={{ background: 'white', borderColor: 'var(--border)' }}
          />
        </div>
        <button
          onClick={() => setShowFilters(s => !s)}
          className="w-12 h-12 rounded-full flex items-center justify-center border transition-all"
          style={{ background: showFilters ? 'var(--text-primary)' : 'white', borderColor: 'var(--border)' }}
        >
          <SlidersHorizontal size={18} color={showFilters ? '#fff' : 'var(--text-secondary)'} />
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="bg-white rounded-2xl p-5 mb-5 border" style={{ borderColor: 'var(--border)' }}>
          <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>Opportunity Type</p>
          <div className="flex flex-wrap gap-2">
            {opportunityTypes.map(t => (
              <button key={t} onClick={() => toggleType(t)}
                className="px-3 py-1.5 rounded-full text-xs border capitalize"
                style={{
                  background: filterType.includes(t) ? 'var(--text-primary)' : 'transparent',
                  color: filterType.includes(t) ? '#fff' : 'var(--text-secondary)',
                  borderColor: 'var(--border)',
                }}>
                {typeLabels[t]}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {categoryTabs.map(cat => {
          const catLabel = cat.label === 'All Categories' ? 'All' : cat.label;
          return (
            <button key={cat.id} onClick={() => setActiveFilter(catLabel)}
              className="px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-all"
              style={{
                background: activeFilter === catLabel ? 'var(--text-primary)' : 'white',
                color: activeFilter === catLabel ? '#fff' : 'var(--text-primary)',
                borderColor: activeFilter === catLabel ? 'var(--text-primary)' : 'var(--border)',
              }}>
              {cat.icon && <span className="mr-2">{cat.icon}</span>}
              {cat.label}
            </button>
          );
        })}
      </div>

      {error && <p className="text-sm py-10 text-center" style={{ color: 'var(--red)' }}>{error}</p>}

      {!error && (
        <>
          {!loading && <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>{displayJobs.length} opportunities found</p>}
          <div className="flex flex-col gap-4">
            {loading 
              ? Array.from({ length: 5 }).map((_, i) => <JobCardWideSkeleton key={i} />)
              : displayJobs.map(job => <JobCardWide key={job.id} job={job} />)
            }
            {!loading && displayJobs.length === 0 && (
              <p className="text-center py-10" style={{ color: 'var(--text-muted)' }}>
                No opportunities match your search.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
