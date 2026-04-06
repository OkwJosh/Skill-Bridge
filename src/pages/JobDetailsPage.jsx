import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Share2, Users, Clock, MapPin, Bookmark } from 'lucide-react';
import { jobs, formatSalary } from '../data';
import { CompanyLogo, Button, PageHeader, Badge } from '../components/UI';

const tabs = ['Job Information', 'Requirements', 'About Company'];

export default function JobDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const job = jobs.find(j => j.id === Number(id)) || jobs[0];
  const [activeTab, setActiveTab] = useState(0);
  const [saved, setSaved] = useState(false);

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader
        title="Job Details"
        onBack
        rightSlot={
          <button className="w-9 h-9 rounded-full border flex items-center justify-center hover:bg-gray-50" style={{ borderColor: 'var(--border)' }}>
            <Share2 size={16} />
          </button>
        }
      />

      <div className="flex gap-6 items-start">
        {/* Main content */}
        <div className="flex-1 min-w-0">
          {/* Hero card */}
          <div className="rounded-2xl p-6 text-center mb-5" style={{ background: 'var(--text-primary)' }}>
            <div className="flex justify-center mb-3">
              <CompanyLogo companyKey={job.companyKey} size={56} />
            </div>
            <h2 className="text-xl font-bold text-white mb-1">{job.title}</h2>
            <p className="text-sm mb-1" style={{ color: '#9CA3AF' }}>{job.company}</p>
            <p className="text-sm mb-3" style={{ color: '#9CA3AF' }}>{job.type} · {job.mode}</p>
            <p className="text-lg font-bold text-white">{formatSalary(job.salaryMin, job.salaryMax)}</p>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mb-5">
            {[
              { icon: Users, label: `${job.applicants}+ Applicants` },
              { icon: Clock, label: `${job.daysLeft} Days Left` },
              { icon: MapPin, label: job.location },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="bg-white rounded-xl p-3 flex flex-col items-center gap-1 border" style={{ borderColor: 'var(--border)' }}>
                <Icon size={18} style={{ color: 'var(--text-muted)' }} />
                <p className="text-xs text-center" style={{ color: 'var(--text-secondary)' }}>{label}</p>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div className="flex gap-0 mb-5 border-b" style={{ borderColor: 'var(--border)' }}>
            {tabs.map((tab, i) => (
              <button
                key={tab}
                onClick={() => setActiveTab(i)}
                className="px-4 py-3 text-sm font-medium transition-colors"
                style={{
                  color: activeTab === i ? 'var(--text-primary)' : 'var(--text-muted)',
                  borderBottom: activeTab === i ? '2px solid var(--text-primary)' : '2px solid transparent',
                  marginBottom: -1,
                }}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 0 && (
            <div>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>📋 Job Description</h3>
              <p className="text-sm leading-relaxed mb-4" style={{ color: 'var(--text-secondary)' }}>{job.description}</p>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Responsibilities</h3>
              <ul className="flex flex-col gap-2">
                {job.responsibilities.map((r, i) => (
                  <li key={i} className="flex gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--text-muted)' }}>·</span>{r}
                  </li>
                ))}
              </ul>
              <p className="text-sm mt-4" style={{ color: 'var(--text-muted)' }}>
                Deadline <span className="float-right font-medium" style={{ color: 'var(--text-primary)' }}>{job.deadline}</span>
              </p>
            </div>
          )}
          {activeTab === 1 && (
            <div>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Requirements</h3>
              <ul className="flex flex-col gap-2">
                {job.requirements.map((r, i) => (
                  <li key={i} className="flex gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--text-muted)' }}>·</span>{r}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {activeTab === 2 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <CompanyLogo companyKey={job.companyKey} size={48} />
                <div>
                  <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{job.company}</p>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{job.location}</p>
                </div>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{job.aboutCompany}</p>
            </div>
          )}
        </div>

        {/* Sidebar action card */}
        <div className="w-56 shrink-0">
          <div className="bg-white rounded-2xl p-5 border sticky top-8" style={{ borderColor: 'var(--border)' }}>
            <p className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>Interested in this role?</p>
            <div className="flex flex-col gap-2 mb-5 text-sm">
              {[
                { label: 'Salary', value: formatSalary(job.salaryMin, job.salaryMax) },
                { label: 'Type', value: job.type },
                { label: 'Mode', value: job.mode },
                { label: 'Deadline', value: job.deadline },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between">
                  <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{value}</span>
                </div>
              ))}
            </div>
            <Button onClick={() => navigate(`/app/jobs/${job.id}/apply`)} className="mb-2">Apply Now</Button>
            <button
              onClick={() => setSaved(s => !s)}
              className="w-full py-3 rounded-full border flex items-center justify-center gap-2 text-sm font-medium hover:bg-gray-50"
              style={{ borderColor: 'var(--border)', color: saved ? 'var(--text-primary)' : 'var(--text-secondary)' }}
            >
              <Bookmark size={15} fill={saved ? 'currentColor' : 'none'} />
              {saved ? 'Saved' : 'Save Job'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
