import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Dashboard, PlayArrow, History, Shield } from '@mui/icons-material';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: <Dashboard />, label: 'Dashboard' },
    { path: '/intent', icon: <PlayArrow />, label: 'Submit Intent' },
    { path: '/audit', icon: <History />, label: 'Audit Log' },
    { path: '/tarl', icon: <Shield />, label: 'TARL Rules' },
  ];

  return (
    <Box
      sx={{
        width: 240,
        bgcolor: '#1E1E2E',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
            sx={{
              mx: 1,
              borderRadius: 2,
              mb: 0.5,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
};

export default Sidebar;
