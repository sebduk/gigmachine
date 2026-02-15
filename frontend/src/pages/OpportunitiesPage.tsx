import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { FundingOpportunity, PaginatedResponse } from '../types';

const cardStyle: React.CSSProperties = {
  border: '1px solid #e0e0e0',
  borderRadius: '8px',
  padding: '1.25rem',
  marginBottom: '1rem',
  backgroundColor: '#fff',
};

const tagStyle: React.CSSProperties = {
  display: 'inline-block',
  padding: '0.15rem 0.5rem',
  backgroundColor: '#eff6ff',
  color: '#1d4ed8',
  borderRadius: '12px',
  fontSize: '0.8rem',
  marginRight: '0.4rem',
  marginTop: '0.3rem',
};

function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<FundingOpportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data: PaginatedResponse<FundingOpportunity> = await api.getOpportunities(page);
        setOpportunities(data.items);
        setTotal(data.total);
      } catch {
        // API may not be running
      }
      setLoading(false);
    }
    load();
  }, [page]);

  if (loading) return <p>Loading opportunities...</p>;

  return (
    <div>
      <h1>Funding Opportunities</h1>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        {total} opportunities from our network of funding sources.
      </p>

      {opportunities.length === 0 ? (
        <div style={cardStyle}>
          <p>No opportunities yet. They will appear here as our scrapers discover them.</p>
        </div>
      ) : (
        opportunities.map(opp => (
          <div key={opp.id} style={cardStyle}>
            <h3 style={{ margin: '0 0 0.5rem' }}>
              <a href={opp.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1d4ed8' }}>
                {opp.title}
              </a>
            </h3>
            <div style={{ display: 'flex', gap: '1.5rem', color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              {opp.funder && <span>Funder: {opp.funder}</span>}
              {opp.deadline && <span>Deadline: {opp.deadline}</span>}
              {(opp.budget_min || opp.budget_max) && (
                <span>
                  Budget: {opp.budget_min && `${opp.currency} ${opp.budget_min}`}
                  {opp.budget_min && opp.budget_max && ' - '}
                  {opp.budget_max && `${opp.currency} ${opp.budget_max}`}
                </span>
              )}
            </div>
            {opp.description && (
              <p style={{ color: '#444', fontSize: '0.95rem', margin: '0.5rem 0' }}>
                {opp.description.slice(0, 300)}{opp.description.length > 300 ? '...' : ''}
              </p>
            )}
            <div>
              {opp.keywords.map(k => (
                <span key={k.id} style={tagStyle}>{k.value}</span>
              ))}
              {opp.fields.map(f => (
                <span key={f.id} style={{ ...tagStyle, backgroundColor: '#f0fdf4', color: '#166534' }}>
                  {f.name}
                </span>
              ))}
            </div>
          </div>
        ))
      )}

      {total > 20 && (
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1rem' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{ padding: '0.5rem 1rem', cursor: page === 1 ? 'not-allowed' : 'pointer' }}
          >
            Previous
          </button>
          <span style={{ padding: '0.5rem' }}>Page {page} of {Math.ceil(total / 20)}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / 20)}
            style={{ padding: '0.5rem 1rem', cursor: page >= Math.ceil(total / 20) ? 'not-allowed' : 'pointer' }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default OpportunitiesPage;
