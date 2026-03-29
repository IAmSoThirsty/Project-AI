import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { AccountCircle, Texture } from '@mui/icons-material';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/');
  };

  return (
    <AppBar position="static" elevation={0}>
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          component={RouterLink}
          to="/"
          sx={{ mr: 2 }}
        >
          <Texture />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4 }}>
          TTP
        </Typography>

        <Box sx={{ flexGrow: 1, display: 'flex', gap: 2 }}>
          <Button color="inherit" component={RouterLink} to="/packs">
            Browse Packs
          </Button>
        </Box>

        {isAuthenticated ? (
          <>
            <Typography variant="body2" sx={{ mr: 2 }}>
              {user?.username}
            </Typography>
            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={() => { navigate('/profile'); handleClose(); }}>
                Profile
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </>
        ) : (
          <>
            <Button color="inherit" component={RouterLink} to="/login">
              Login
            </Button>
            <Button
              variant="outlined"
              color="inherit"
              component={RouterLink}
              to="/register"
              sx={{ ml: 1 }}
            >
              Register
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
