import { Link } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  return (
    <div className="dashboard">
      <nav className="sidebar">
        <h2>Project-AI</h2>
        <ul>
          <li>
            <Link to="/dashboard">Dashboard</Link>
          </li>
          <li>
            <Link to="/users">User Management</Link>
          </li>
          <li>
            <Link to="/image-gen">Image Generation</Link>
          </li>
          <li>
            <Link to="/analysis">Data Analysis</Link>
          </li>
          <li>
            <Link to="/learning">Learning Paths</Link>
          </li>
          <li>
            <Link to="/security">Security Resources</Link>
          </li>
        </ul>
      </nav>
      <main className="content">
        <h1>Dashboard</h1>
        <div className="cards">
          <div className="card">
            <h3>Total Users</h3>
            <p className="stat">0</p>
          </div>
          <div className="card">
            <h3>Active Sessions</h3>
            <p className="stat">0</p>
          </div>
          <div className="card">
            <h3>Images Generated</h3>
            <p className="stat">0</p>
          </div>
          <div className="card">
            <h3>Analyses Completed</h3>
            <p className="stat">0</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
