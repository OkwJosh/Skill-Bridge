import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, Button } from '../components/UI';
import { skillsList } from '../data';
import { Search } from 'lucide-react';

const experienceLevels = ['Intern', 'Junior', 'Mid Level', 'Senior'];

export default function AddSkillsPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(['Programming', 'Design', 'Marketing']);
  const [level, setLevel] = useState('Junior');
  const [query, setQuery] = useState('');

  const toggle = (skill) => {
    setSelected(s => s.includes(skill) ? s.filter(x => x !== skill) : [...s, skill]);
  };

  return (
    <AuthShell>
      <div className="w-full max-w-sm mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center" style={{ fontFamily: "'DM Serif Display', serif" }}>
          Add your<br />skills
        </h1>
        <p className="text-sm text-center mb-6" style={{ color: 'var(--text-secondary)' }}>
          Improve your job matches by listing your professional skills.
        </p>

        {/* Search */}
        <div className="relative mb-4">
          <Search size={14} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            placeholder="Type a skill (e.g., React, UI UX)"
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-full text-sm border"
            style={{ background: '#F9F9F7', borderColor: 'var(--border)' }}
          />
        </div>

        {/* Skill chips */}
        <div className="flex flex-wrap gap-2 mb-6">
          {skillsList
            .filter(s => s.toLowerCase().includes(query.toLowerCase()))
            .map(skill => (
              <button
                key={skill}
                onClick={() => toggle(skill)}
                className="px-4 py-2 rounded-full text-sm font-medium border transition-all"
                style={{
                  background: selected.includes(skill) ? 'var(--text-primary)' : 'transparent',
                  color: selected.includes(skill) ? '#fff' : 'var(--text-primary)',
                  borderColor: selected.includes(skill) ? 'var(--text-primary)' : 'var(--border)',
                }}
              >
                {skill}
              </button>
            ))}
        </div>

        {/* Experience level */}
        <div className="mb-6">
          <p className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>Experience Level</p>
          <div className="flex flex-col gap-2">
            {experienceLevels.map(l => (
              <label key={l} className="flex items-center gap-3 cursor-pointer">
                <div
                  onClick={() => setLevel(l)}
                  className="w-5 h-5 rounded-full border-2 flex items-center justify-center cursor-pointer"
                  style={{ borderColor: level === l ? 'var(--text-primary)' : 'var(--border)' }}
                >
                  {level === l && <div className="w-2.5 h-2.5 rounded-full" style={{ background: 'var(--text-primary)' }} />}
                </div>
                <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{l}</span>
              </label>
            ))}
          </div>
        </div>

        <Button onClick={() => navigate('/account-success')} className="mb-2">Let's Start</Button>
        <Button variant="ghost" onClick={() => navigate('/account-success')}>Skip for Now</Button>
      </div>
    </AuthShell>
  );
}
