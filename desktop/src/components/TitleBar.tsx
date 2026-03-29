import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { Close, Minimize, CropSquare } from '@mui/icons-material';

interface TitleBarProps {
  onCloseRequest?: () => void;
}

const TitleBar: React.FC<TitleBarProps> = ({ onCloseRequest }) => {
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
    if (onCloseRequest) {
      onCloseRequest();
      return;
    }

    if (window.electron) {
      window.electron.window.close();
    }
  };

  return (
    <Box
      sx={{
        height: 44,
        bgcolor: '#161b13',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 2.2,
        WebkitAppRegion: 'drag',
        borderBottom: '2px solid rgba(96, 117, 87, 0.9)',
      }}
    >
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 700, color: '#f5e6a6', letterSpacing: 0.8 }}>
          Sovereign Cognitive IDE
        </Typography>
        <Typography variant="caption" sx={{ color: '#b6c0a6', display: 'block', mt: -0.1 }}>
          Local workstation for Sovereign-Governance-Substrate
        </Typography>
      </Box>
      <Box sx={{ WebkitAppRegion: 'no-drag', display: 'flex', gap: 0.5 }}>
        <IconButton size="small" onClick={handleMinimize} sx={{ color: '#edf2d0' }}>
          <Minimize fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={handleMaximize} sx={{ color: '#edf2d0' }}>
          <CropSquare fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={handleClose} sx={{ color: '#f5b1a1' }}>
          <Close fontSize="small" />
        </IconButton>
      </Box>
    </Box>
  );
};

export default TitleBar;
