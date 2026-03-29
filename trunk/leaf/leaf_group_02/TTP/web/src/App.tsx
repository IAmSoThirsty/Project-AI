import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import PacksPage from './pages/PacksPage';
import PackDetailPage from './pages/PackDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="packs" element={<PacksPage />} />
          <Route path="packs/:packId" element={<PackDetailPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
