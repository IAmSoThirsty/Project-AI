import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { Close, Minimize, CropSquare } from '@mui/icons-material';

const TitleBar: React.FC = () => {
  const handleMinimize = () => {
    if (window.electron) {
      window.electron.window.minimize();
    }
  };

  const handleMaximize = () => {
    if (window.electron) {
      window.electron.window.maximize();
    }
  };

  const handleClose = () => {
    if (window.electron) {
      window.electron.window.close();
    }
  };

  return (
    <Box
      sx={{
        height: 40,
        bgcolor: '#1E1E2E',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 2,
        WebkitAppRegion: 'drag',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
      }}
    >
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        Project <span style={{ color: '#7C7CFF' }}>AI</span> - Governance Desktop
      </Typography>
      <Box sx={{ WebkitAppRegion: 'no-drag', display: 'flex', gap: 0.5 }}>
        <IconButton size="small" onClick={handleMinimize} sx={{ color: 'white' }}>
          <Minimize fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={handleMaximize} sx={{ color: 'white' }}>
          <CropSquare fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={handleClose} sx={{ color: 'white' }}>
          <Close fontSize="small" />
        </IconButton>
      </Box>
    </Box>
  );
};

export default TitleBar;
