import { Navigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
} from '@mui/material';
import { useAuthStore } from '@/store/authStore';

export default function ProfilePage() {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>

      <Card sx={{ maxWidth: 600, mt: 3 }}>
        <CardContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Username
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {user?.username}
            </Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Email
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Role
            </Typography>
            <Chip label={user?.role} color="primary" />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Member Since
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </Typography>
          </Box>

          {user?.last_login && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Last Login
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {new Date(user.last_login).toLocaleString()}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
