import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
} from '@mui/material';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { userApi } from '@/lib/api';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (data) => {
      const user = await userApi.getCurrentUser();
      login(user, data.access_token);
      toast.success('Login successful!');
      navigate('/packs');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate({ username, password });
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh',
      }}
    >
      <Card sx={{ maxWidth: 450, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom align="center">
            Login
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Sign in to your account
          </Typography>

          {loginMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Invalid username or password
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              label="Username"
              variant="outlined"
              fullWidth
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{ mb: 2 }}
              required
            />
            <TextField
              label="Password"
              type="password"
              variant="outlined"
              fullWidth
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 3 }}
              required
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2">
              Don't have an account?{' '}
              <Link component={RouterLink} to="/register">
                Register
              </Link>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
