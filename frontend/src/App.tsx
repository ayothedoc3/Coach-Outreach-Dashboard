import { BrowserRouter as Router } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function AppContent() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!token) {
    return <Login />;
  }

  return <Dashboard />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <AppContent />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
