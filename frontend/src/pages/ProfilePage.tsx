import { useEffect, useState, type FormEvent } from 'react';
import { api } from '../api/client';
import type { AcademicProfile, CareerStage } from '../types';

const formStyle: React.CSSProperties = {
  maxWidth: '600px',
  display: 'flex',
  flexDirection: 'column',
  gap: '1rem',
};

const inputStyle: React.CSSProperties = {
  padding: '0.5rem',
  borderRadius: '4px',
  border: '1px solid #ccc',
  fontSize: '1rem',
};

const labelStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.25rem',
  fontWeight: 500,
};

const CAREER_STAGES: { value: CareerStage; label: string }[] = [
  { value: 'phd_student', label: 'PhD Student' },
  { value: 'postdoc', label: 'Postdoc' },
  { value: 'early_career', label: 'Early Career' },
  { value: 'mid_career', label: 'Mid Career' },
  { value: 'senior', label: 'Senior' },
  { value: 'emeritus', label: 'Emeritus' },
];

function ProfilePage() {
  const [profile, setProfile] = useState<AcademicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [careerStage, setCareerStage] = useState<CareerStage | ''>('');
  const [institution, setInstitution] = useState('');
  const [department, setDepartment] = useState('');
  const [bio, setBio] = useState('');
  const [publications, setPublications] = useState('');
  const [orcid, setOrcid] = useState('');
  const [keywords, setKeywords] = useState('');
  const [fields, setFields] = useState('');
  const [threshold, setThreshold] = useState(0.5);

  useEffect(() => {
    async function load() {
      try {
        const profiles = await api.getProfiles();
        if (profiles.length > 0) {
          const p = profiles[0];
          setProfile(p);
          setName(p.name);
          setEmail(p.email);
          setCareerStage(p.career_stage || '');
          setInstitution(p.institution || '');
          setDepartment(p.department || '');
          setBio(p.bio || '');
          setPublications(p.publications_summary || '');
          setOrcid(p.orcid || '');
          setKeywords(p.keywords.map(k => k.value).join(', '));
          setFields(p.fields.map(f => f.name).join(', '));
          setThreshold(p.match_threshold);
        }
      } catch {
        // API may not be running
      }
      setLoading(false);
    }
    load();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    const data = {
      name,
      email,
      career_stage: careerStage || null,
      institution: institution || null,
      department: department || null,
      bio: bio || null,
      publications_summary: publications || null,
      orcid: orcid || null,
      keyword_values: keywords.split(',').map(k => k.trim()).filter(Boolean),
      field_names: fields.split(',').map(f => f.trim()).filter(Boolean),
      match_threshold: threshold,
    };

    try {
      if (profile) {
        await api.updateProfile(profile.id, data);
        setMessage('Profile updated successfully.');
      } else {
        const created = await api.createProfile(data);
        setProfile(created);
        setMessage('Profile created successfully.');
      }
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setSaving(false);
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>{profile ? 'Edit Your Profile' : 'Create Your Profile'}</h1>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Tell us about your research so we can find the right funding opportunities.
      </p>

      {message && (
        <div style={{
          padding: '0.75rem',
          borderRadius: '4px',
          marginBottom: '1rem',
          backgroundColor: message.startsWith('Error') ? '#fee2e2' : '#dcfce7',
          color: message.startsWith('Error') ? '#991b1b' : '#166534',
        }}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} style={formStyle}>
        <label style={labelStyle}>
          Name *
          <input style={inputStyle} value={name} onChange={e => setName(e.target.value)} required />
        </label>

        <label style={labelStyle}>
          Email *
          <input style={inputStyle} type="email" value={email} onChange={e => setEmail(e.target.value)} required disabled={!!profile} />
        </label>

        <label style={labelStyle}>
          Career Stage
          <select style={inputStyle} value={careerStage} onChange={e => setCareerStage(e.target.value as CareerStage)}>
            <option value="">Select...</option>
            {CAREER_STAGES.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>

        <label style={labelStyle}>
          Institution
          <input style={inputStyle} value={institution} onChange={e => setInstitution(e.target.value)} />
        </label>

        <label style={labelStyle}>
          Department
          <input style={inputStyle} value={department} onChange={e => setDepartment(e.target.value)} />
        </label>

        <label style={labelStyle}>
          Bio
          <textarea style={{ ...inputStyle, minHeight: '80px' }} value={bio} onChange={e => setBio(e.target.value)} placeholder="Brief description of your research interests and expertise..." />
        </label>

        <label style={labelStyle}>
          Key Publications
          <textarea style={{ ...inputStyle, minHeight: '60px' }} value={publications} onChange={e => setPublications(e.target.value)} placeholder="Summary of your key publications..." />
        </label>

        <label style={labelStyle}>
          ORCID
          <input style={inputStyle} value={orcid} onChange={e => setOrcid(e.target.value)} placeholder="0000-0000-0000-0000" />
        </label>

        <label style={labelStyle}>
          Keywords (comma-separated)
          <input style={inputStyle} value={keywords} onChange={e => setKeywords(e.target.value)} placeholder="machine learning, genomics, climate science..." />
        </label>

        <label style={labelStyle}>
          Research Fields (comma-separated)
          <input style={inputStyle} value={fields} onChange={e => setFields(e.target.value)} placeholder="Computer Science, Biology, Environmental Science..." />
        </label>

        <label style={labelStyle}>
          Match Threshold ({Math.round(threshold * 100)}%)
          <input type="range" min="0" max="1" step="0.05" value={threshold} onChange={e => setThreshold(parseFloat(e.target.value))} />
          <span style={{ color: '#666', fontSize: '0.85rem' }}>
            Only show matches scoring above this threshold
          </span>
        </label>

        <button
          type="submit"
          disabled={saving}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '1rem',
            cursor: saving ? 'not-allowed' : 'pointer',
            opacity: saving ? 0.7 : 1,
          }}
        >
          {saving ? 'Saving...' : (profile ? 'Update Profile' : 'Create Profile')}
        </button>
      </form>
    </div>
  );
}

export default ProfilePage;
