import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import TitleBar from './components/TitleBar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Intent from './pages/Intent';
import Audit from './pages/Audit';
import Tarl from './pages/Tarl';

const App: React.FC = () => {
  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      overflow: 'hidden',
      background: 'radial-gradient(circle at 50% 50%, #1a1a2a 0%, #050505 100%)'
    }}>
      <TitleBar />
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden', p: 1 }}>
        <Sidebar className="sovereign-glass" />
        <Box sx={{
          flex: 1,
          overflow: 'auto',
          p: 3,
          m: 1,
          className: 'sovereign-glass'
        }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/intent" element={<Intent />} />
            <Route path="/audit" element={<Audit />} />
            <Route path="/tarl" element={<Tarl />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  );
};

export default App;
