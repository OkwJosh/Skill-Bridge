import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, SlidersHorizontal } from 'lucide-react';
import { jobs, categories, currentUser } from '../data';
import { JobCardSmall, JobCardWide, SectionHeader, Avatar } from '../components/UI';

export default function HomePage() {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState(null);

  const recentJobs = jobs.slice(0, 4);
  const recommendedJobs = jobs.slice(0, 6);

  return (
    <div className="p-8 max-w-5xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <Avatar name={currentUser.name} size={44} />
          <div>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Welcome back</p>
            <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{currentUser.name} 👋</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/app/notifications')}
          className="relative w-10 h-10 rounded-full border flex items-center justify-center hover:bg-gray-50"
          style={{ borderColor: 'var(--border)' }}
        >
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500" />
        </button>
      </div>

      {/* Title + Search */}
      <h1 className="text-2xl font-bold mb-5" style={{ color: 'var(--text-primary)' }}>
        Explore Top Jobs Around You
      </h1>

      <div className="flex gap-2 mb-8">
        <div className="flex-1 relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2" width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="7" stroke="#9CA3AF" strokeWidth="2"/>
            <path d="M16.5 16.5L21 21" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <input
            placeholder="Search Job..."
            className="w-full pl-11 pr-4 py-3 rounded-full text-sm border"
            style={{ background: 'white', borderColor: 'var(--border)' }}
            onFocus={() => navigate('/app/search')}
            readOnly
          />
        </div>
        <button
          onClick={() => navigate('/app/jobs')}
          className="w-12 h-12 rounded-full flex items-center justify-center border"
          style={{ background: 'white', borderColor: 'var(--border)' }}
        >
          <SlidersHorizontal size={18} style={{ color: 'var(--text-secondary)' }} />
        </button>
      </div>

      {/* Categories */}
      <div className="mb-8">
        <SectionHeader title="Categories" onSeeAll={() => navigate('/app/jobs')} />
        <div className="flex flex-wrap gap-2">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
              className="px-4 py-2 rounded-full text-sm border transition-all"
              style={{
                background: activeCategory === cat.id ? 'var(--text-primary)' : 'white',
                color: activeCategory === cat.id ? '#fff' : 'var(--text-primary)',
                borderColor: activeCategory === cat.id ? 'var(--text-primary)' : 'var(--border)',
              }}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="mb-8">
        <SectionHeader title="Recent Jobs" onSeeAll={() => navigate('/app/jobs')} />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {recentJobs.map(job => (
            <JobCardSmall key={job.id} job={job} />
          ))}
        </div>
      </div>

      {/* Recommended Jobs */}
      <div>
        <SectionHeader title="Recommended Jobs" onSeeAll={() => navigate('/app/jobs')} />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendedJobs.map(job => (
            <JobCardWide key={job.id} job={job} />
          ))}
        </div>
      </div>
    </div>
  );
}
