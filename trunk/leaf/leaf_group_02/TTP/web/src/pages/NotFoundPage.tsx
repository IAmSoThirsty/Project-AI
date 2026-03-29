import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';
import { Home } from '@mui/icons-material';

export default function NotFoundPage() {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
      }}
    >
      <Typography variant="h1" sx={{ fontSize: '6rem', fontWeight: 700 }}>
        404
      </Typography>
      <Typography variant="h5" gutterBottom>
        Page Not Found
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        The page you're looking for doesn't exist.
      </Typography>
      <Button
        variant="contained"
        component={RouterLink}
        to="/"
        startIcon={<Home />}
        sx={{ mt: 2 }}
      >
        Go Home
      </Button>
    </Box>
  );
}
