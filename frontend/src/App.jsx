import { useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './styles/App.css';

function App() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return <Dashboard user={user} onLogout={logout} />;
}

export default App;
