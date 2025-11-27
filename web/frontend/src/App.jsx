import { useState } from 'react';
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import DataAnalysis from './components/DataAnalysis';
import ImageGeneration from './components/ImageGeneration';
import LearningPaths from './components/LearningPaths';
import Login from './components/Login';
import SecurityResources from './components/SecurityResources';
import UserManagement from './components/UserManagement';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route
            path="/login"
            element={<Login onLogin={() => setIsAuthenticated(true)} />}
          />
          <Route
            path="/dashboard"
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/users"
            element={
              isAuthenticated ? <UserManagement /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/image-gen"
            element={
              isAuthenticated ? <ImageGeneration /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/analysis"
            element={
              isAuthenticated ? <DataAnalysis /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/learning"
            element={
              isAuthenticated ? <LearningPaths /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/security"
            element={
              isAuthenticated ? <SecurityResources /> : <Navigate to="/login" />
            }
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
