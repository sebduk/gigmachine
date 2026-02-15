import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage';
import OpportunitiesPage from './pages/OpportunitiesPage';
import MatchesPage from './pages/MatchesPage';

const navStyle: React.CSSProperties = {
  display: 'flex',
  gap: '1.5rem',
  padding: '1rem 2rem',
  borderBottom: '1px solid #e0e0e0',
  backgroundColor: '#f8f9fa',
  fontFamily: 'system-ui, -apple-system, sans-serif',
};

const linkStyle: React.CSSProperties = {
  textDecoration: 'none',
  color: '#333',
  fontWeight: 500,
};

const mainStyle: React.CSSProperties = {
  maxWidth: '1200px',
  margin: '0 auto',
  padding: '2rem',
  fontFamily: 'system-ui, -apple-system, sans-serif',
};

function App() {
  return (
    <>
      <nav style={navStyle}>
        <Link to="/" style={{ ...linkStyle, fontWeight: 700, fontSize: '1.2rem' }}>
          GigFinder
        </Link>
        <Link to="/profile" style={linkStyle}>My Profile</Link>
        <Link to="/opportunities" style={linkStyle}>Opportunities</Link>
        <Link to="/matches" style={linkStyle}>My Matches</Link>
      </nav>
      <main style={mainStyle}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/opportunities" element={<OpportunitiesPage />} />
          <Route path="/matches" element={<MatchesPage />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
