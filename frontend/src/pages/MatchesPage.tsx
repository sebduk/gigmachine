import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Match, PaginatedResponse } from '../types';

const cardStyle: React.CSSProperties = {
  border: '1px solid #e0e0e0',
  borderRadius: '8px',
  padding: '1.25rem',
  marginBottom: '1rem',
  backgroundColor: '#fff',
  display: 'flex',
  gap: '1rem',
};

const scoreStyle = (score: number): React.CSSProperties => ({
  minWidth: '60px',
  height: '60px',
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontWeight: 700,
  fontSize: '1.1rem',
  backgroundColor: score >= 0.7 ? '#dcfce7' : score >= 0.4 ? '#fef9c3' : '#fee2e2',
  color: score >= 0.7 ? '#166534' : score >= 0.4 ? '#854d0e' : '#991b1b',
  flexShrink: 0,
});

const btnStyle: React.CSSProperties = {
  padding: '0.3rem 0.7rem',
  border: '1px solid #ccc',
  borderRadius: '4px',
  backgroundColor: '#fff',
  cursor: 'pointer',
  fontSize: '0.85rem',
};

function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [profileId, setProfileId] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const profiles = await api.getProfiles();
        if (profiles.length > 0) {
          setProfileId(profiles[0].id);
          const data: PaginatedResponse<Match> = await api.getMatches(profiles[0].id, page);
          setMatches(data.items);
          setTotal(data.total);
        }
      } catch {
        // API may not be running
      }
      setLoading(false);
    }
    load();
  }, [page]);

  const handleRefresh = async () => {
    if (!profileId) return;
    setRefreshing(true);
    try {
      const result = await api.refreshMatches(profileId);
      alert(`Found ${result.new_matches} new matches!`);
      // Reload
      const data: PaginatedResponse<Match> = await api.getMatches(profileId, page);
      setMatches(data.items);
      setTotal(data.total);
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setRefreshing(false);
  };

  const handleAction = async (matchId: number, action: Record<string, boolean>) => {
    if (!profileId) return;
    try {
      const updated = await api.updateMatch(profileId, matchId, action);
      setMatches(ms => ms.map(m => m.id === matchId ? updated : m));
    } catch {
      // ignore
    }
  };

  const parseReasons = (reasons: string | null): Array<{ type: string; detail: unknown; score: number }> => {
    if (!reasons) return [];
    try { return JSON.parse(reasons); } catch { return []; }
  };

  if (loading) return <p>Loading matches...</p>;
  if (!profileId) return <p>Create a profile first to see matches.</p>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Your Matches</h1>
          <p style={{ color: '#666', margin: '0.25rem 0 0' }}>
            {total} opportunities matched to your profile.
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          style={{
            ...btnStyle,
            backgroundColor: '#2563eb',
            color: '#fff',
            border: 'none',
            padding: '0.5rem 1rem',
          }}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Matches'}
        </button>
      </div>

      {matches.length === 0 ? (
        <p style={{ color: '#666' }}>No matches yet. Click &quot;Refresh Matches&quot; to scan for opportunities.</p>
      ) : (
        matches.filter(m => !m.is_dismissed).map(m => (
          <div key={m.id} style={cardStyle}>
            <div style={scoreStyle(m.score)}>
              {Math.round(m.score * 100)}%
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ margin: '0 0 0.25rem' }}>
                <a href={m.opportunity.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1d4ed8' }}>
                  {m.opportunity.title}
                </a>
              </h3>
              <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                {m.opportunity.funder && <span>{m.opportunity.funder}</span>}
                {m.opportunity.deadline && <span> | Due: {m.opportunity.deadline}</span>}
              </div>
              {m.opportunity.description && (
                <p style={{ color: '#444', fontSize: '0.9rem', margin: '0.5rem 0' }}>
                  {m.opportunity.description.slice(0, 200)}{m.opportunity.description.length > 200 ? '...' : ''}
                </p>
              )}
              <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                <strong>Why this match: </strong>
                {parseReasons(m.match_reasons)
                  .filter(r => r.score > 0)
                  .map(r => `${r.type.replace('_', ' ')} (${Math.round(r.score * 100)}%)`)
                  .join(', ')
                }
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                <button
                  onClick={() => handleAction(m.id, { is_saved: !m.is_saved })}
                  style={{
                    ...btnStyle,
                    backgroundColor: m.is_saved ? '#dbeafe' : '#fff',
                    borderColor: m.is_saved ? '#2563eb' : '#ccc',
                  }}
                >
                  {m.is_saved ? 'Saved' : 'Save'}
                </button>
                <button
                  onClick={() => handleAction(m.id, { is_dismissed: true })}
                  style={btnStyle}
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        ))
      )}

      {total > 20 && (
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1rem' }}>
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={btnStyle}>
            Previous
          </button>
          <span style={{ padding: '0.5rem' }}>Page {page} of {Math.ceil(total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)} style={btnStyle}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default MatchesPage;
