import { Outlet } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Navbar from './Navbar';
import Footer from './Footer';

export default function Layout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container component="main" maxWidth="xl" sx={{ flex: 1, py: 4 }}>
        <Outlet />
      </Container>
      <Footer />
    </Box>
  );
}
