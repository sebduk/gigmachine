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

const hintStyle: React.CSSProperties = {
  color: '#666',
  fontSize: '0.85rem',
};

const privacyBoxStyle: React.CSSProperties = {
  padding: '1rem',
  borderRadius: '6px',
  backgroundColor: '#f0fdf4',
  border: '1px solid #bbf7d0',
  marginBottom: '1.5rem',
  fontSize: '0.9rem',
  color: '#166534',
};

const dangerBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  backgroundColor: '#fff',
  color: '#dc2626',
  border: '1px solid #dc2626',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '0.9rem',
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

  const [handle, setHandle] = useState('');
  const [email, setEmail] = useState('');
  const [careerStage, setCareerStage] = useState<CareerStage | ''>('');
  const [researchSummary, setResearchSummary] = useState('');
  const [keywords, setKeywords] = useState('');
  const [fields, setFields] = useState('');
  const [threshold, setThreshold] = useState(0.5);

  // Document upload
  const [docText, setDocText] = useState('');
  const [docType, setDocType] = useState('cv');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const profiles = await api.getProfiles();
        if (profiles.length > 0) {
          const p = profiles[0];
          setProfile(p);
          setHandle(p.handle);
          setCareerStage(p.career_stage || '');
          setResearchSummary(p.research_summary || '');
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
      handle,
      email,
      career_stage: careerStage || null,
      research_summary: researchSummary || null,
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

  const handleDocUpload = async () => {
    if (!profile || !docText.trim()) return;
    setUploading(true);
    try {
      await api.uploadDocument(profile.id, { source_type: docType, raw_text: docText });
      setMessage('Document processed. Research topics extracted. Original text was not stored.');
      setDocText('');
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setUploading(false);
  };

  const handleDeleteProfile = async () => {
    if (!profile) return;
    if (!confirm('This will permanently delete your profile and all associated data. This cannot be undone.')) return;
    try {
      await api.deleteProfile(profile.id);
      setProfile(null);
      setHandle('');
      setEmail('');
      setMessage('Profile and all data permanently deleted.');
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const handleExportData = async () => {
    if (!profile) return;
    try {
      const data = await api.exportProfileData(profile.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gigfinder-data-export-${profile.handle}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>{profile ? 'Edit Your Profile' : 'Create Your Profile'}</h1>

      <div style={privacyBoxStyle}>
        <strong>Privacy by Design</strong>
        <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.2rem' }}>
          <li>We use handles, not real names. Your identity stays private.</li>
          <li>Your email is for notifications only — never shared or displayed.</li>
          <li>When you upload a CV or publication list, we extract research topics and discard the original. No personal details are stored.</li>
          <li>You can export or permanently delete all your data at any time.</li>
        </ul>
      </div>

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
          Handle *
          <input style={inputStyle} value={handle} onChange={e => setHandle(e.target.value)} required placeholder="Choose a pseudonym (not your real name)" />
          <span style={hintStyle}>This is your public identity on GigFinder. Do not use your real name.</span>
        </label>

        {!profile && (
          <label style={labelStyle}>
            Email *
            <input style={inputStyle} type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="For notifications only — never shared" />
            <span style={hintStyle}>Used solely for match notifications. Never displayed publicly.</span>
          </label>
        )}

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
          Research Interests
          <textarea style={{ ...inputStyle, minHeight: '80px' }} value={researchSummary} onChange={e => setResearchSummary(e.target.value)} placeholder="Describe your research focus, methods, and areas of expertise. Avoid including personal details like your name or institution." />
          <span style={hintStyle}>Describe the work, not the person. Avoid names, institutions, and contact details.</span>
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
          <span style={hintStyle}>Only show matches scoring above this threshold</span>
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

      {profile && (
        <>
          <hr style={{ margin: '2rem 0', borderColor: '#e0e0e0' }} />

          <h2>Upload Research Documents</h2>
          <p style={hintStyle}>
            Paste your CV, publication list, or grant history below. We will extract research topics, methodologies, and domains — then permanently discard the original text. Your name, contact details, and other personal information are stripped before anything is stored.
          </p>
          <div style={{ ...formStyle, marginTop: '1rem' }}>
            <select style={inputStyle} value={docType} onChange={e => setDocType(e.target.value)}>
              <option value="cv">CV / Resume</option>
              <option value="publication">Publication List</option>
              <option value="grant_history">Grant History</option>
            </select>
            <textarea
              style={{ ...inputStyle, minHeight: '120px' }}
              value={docText}
              onChange={e => setDocText(e.target.value)}
              placeholder="Paste document text here. Personal information will be automatically removed..."
            />
            <button
              onClick={handleDocUpload}
              disabled={uploading || !docText.trim()}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#059669',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: uploading ? 'not-allowed' : 'pointer',
                opacity: uploading ? 0.7 : 1,
              }}
            >
              {uploading ? 'Processing...' : 'Process Document (PII stripped)'}
            </button>
          </div>

          <hr style={{ margin: '2rem 0', borderColor: '#e0e0e0' }} />

          <h2>Your Data</h2>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
            <button onClick={handleExportData} style={{ ...dangerBtnStyle, color: '#2563eb', borderColor: '#2563eb' }}>
              Export All My Data
            </button>
            <button onClick={handleDeleteProfile} style={dangerBtnStyle}>
              Permanently Delete Everything
            </button>
          </div>
          <p style={{ ...hintStyle, marginTop: '0.5rem' }}>
            Export downloads a JSON file with everything we hold about you. Deletion is irreversible.
          </p>
        </>
      )}
    </div>
  );
}

export default ProfilePage;
