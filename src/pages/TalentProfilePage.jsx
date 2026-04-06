import { useParams, useNavigate } from 'react-router-dom';
import { Mail } from 'lucide-react';
import { talentProfiles } from '../data';
import { Avatar, Button, PageHeader } from '../components/UI';

export default function TalentProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const talent = talentProfiles.find(t => t.id === Number(id)) || talentProfiles[0];

  return (
    <div className="p-8 max-w-5xl">
      <PageHeader title="Profile" onBack />

      <div className="flex gap-6 items-start">
        {/* Main */}
        <div className="flex-1">
          {/* Profile header */}
          <div className="flex flex-col items-center text-center mb-8">
            <Avatar name={talent.name} size={80} className="mb-3" />
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{talent.name}</h2>
            <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>{talent.role}</p>
            <p className="text-sm mb-2" style={{ color: 'var(--text-muted)' }}>📍 {talent.location}</p>
            <span className="text-sm font-medium px-3 py-1 rounded-full" style={{ background: '#D1FAE5', color: '#065F46' }}>
              {talent.status}
            </span>
          </div>

          {/* About */}
          <section className="mb-6">
            <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>About</h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{talent.about}</p>
          </section>

          {/* Skills */}
          <section className="mb-6">
            <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Skills</h3>
            <div className="flex flex-wrap gap-2">
              {talent.skills.map(skill => (
                <span key={skill} className="px-4 py-2 rounded-full text-sm font-medium text-white" style={{ background: 'var(--text-primary)' }}>
                  {skill}
                </span>
              ))}
            </div>
          </section>

          {/* Portfolio */}
          <section className="mb-6">
            <h3 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Portfolio</h3>
            <div className="grid grid-cols-2 gap-3">
              {[1, 2].map(i => (
                <div key={i} className="h-40 rounded-2xl" style={{ background: '#E5E4E0' }} />
              ))}
            </div>
          </section>

          {/* Education */}
          <section className="mb-4">
            <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Education</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{talent.education}</p>
          </section>

          {/* Experience */}
          <section>
            <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Experience</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{talent.experience}</p>
          </section>
        </div>

        {/* Sidebar */}
        <div className="w-56 shrink-0">
          <div className="bg-white rounded-2xl p-5 border sticky top-8" style={{ borderColor: 'var(--border)' }}>
            <p className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>Contact {talent.name.split(' ')[0]}</p>
            <div className="flex flex-col gap-2 mb-5 text-sm">
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-muted)' }}>Status</span>
                <span className="font-medium text-green-600">{talent.status}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-muted)' }}>Role</span>
                <span className="font-medium text-xs text-right" style={{ color: 'var(--text-primary)', maxWidth: 100 }}>{talent.role}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--text-muted)' }}>Location</span>
                <span className="font-medium text-xs text-right" style={{ color: 'var(--text-primary)', maxWidth: 100 }}>{talent.location}</span>
              </div>
            </div>
            <Button onClick={() => alert('Invite sent!')}>
              <span className="flex items-center justify-center gap-2">
                <Mail size={15} /> Contact / Invite
              </span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
