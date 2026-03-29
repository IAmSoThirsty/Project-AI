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
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success('Registration successful! Please login.');
      navigate('/login');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    registerMutation.mutate({ username, email, password });
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
            Register
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Create your account
          </Typography>

          {registerMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Registration failed. Username or email may already exist.
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
              label="Email"
              type="email"
              variant="outlined"
              fullWidth
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? 'Creating account...' : 'Register'}
            </Button>
          </form>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2">
              Already have an account?{' '}
              <Link component={RouterLink} to="/login">
                Login
              </Link>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
