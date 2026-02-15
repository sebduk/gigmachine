import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { AcademicProfile, Match, PaginatedResponse } from '../types';

const cardStyle: React.CSSProperties = {
  border: '1px solid #e0e0e0',
  borderRadius: '8px',
  padding: '1.5rem',
  marginBottom: '1rem',
  backgroundColor: '#fff',
};

function Dashboard() {
  const [profile, setProfile] = useState<AcademicProfile | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const profiles = await api.getProfiles();
        if (profiles.length > 0) {
          setProfile(profiles[0]);
          const matchData: PaginatedResponse<Match> = await api.getMatches(profiles[0].id);
          setMatches(matchData.items.slice(0, 5));
        }
      } catch {
        // API may not be running yet
      }
      setLoading(false);
    }
    load();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>Welcome to GigFinder</h1>
      <p style={{ color: '#666', fontSize: '1.1rem', marginBottom: '2rem' }}>
        Your talent agent for academic funding opportunities.
        We match your research profile with funding calls so you can focus on the work.
      </p>

      {!profile ? (
        <div style={cardStyle}>
          <h2>Get Started</h2>
          <p>Create your academic profile to start receiving matched opportunities.</p>
          <Link
            to="/profile"
            style={{
              display: 'inline-block',
              padding: '0.5rem 1rem',
              backgroundColor: '#2563eb',
              color: '#fff',
              borderRadius: '6px',
              textDecoration: 'none',
              marginTop: '0.5rem',
            }}
          >
            Create Profile
          </Link>
        </div>
      ) : (
        <>
          <div style={cardStyle}>
            <h2>Your Profile</h2>
            <p><strong>{profile.handle}</strong> — {profile.career_stage || 'Career stage not set'}</p>
            <p>
              Keywords: {profile.keywords.map(k => k.value).join(', ') || 'None set'}
            </p>
            <p>
              Fields: {profile.fields.map(f => f.name).join(', ') || 'None set'}
            </p>
            <Link to="/profile" style={{ color: '#2563eb' }}>Edit profile</Link>
          </div>

          <div style={cardStyle}>
            <h2>Top Matches</h2>
            {matches.length === 0 ? (
              <p style={{ color: '#666' }}>
                No matches yet. Opportunities will be matched as they&apos;re discovered.
              </p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {matches.map(m => (
                  <li key={m.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid #f0f0f0' }}>
                    <strong>{Math.round(m.score * 100)}%</strong>{' '}
                    {m.opportunity.title}
                    {m.opportunity.deadline && (
                      <span style={{ color: '#666', marginLeft: '0.5rem' }}>
                        Due: {m.opportunity.deadline}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
            <Link to="/matches" style={{ color: '#2563eb' }}>View all matches</Link>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
