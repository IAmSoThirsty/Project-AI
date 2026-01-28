import React from 'react';
import { Chip } from '@mui/material';
import { COLORS } from '../config/constants';

interface VerdictBadgeProps {
  verdict: 'allow' | 'deny' | 'degrade' | string;
  size?: 'small' | 'medium';
}

const VerdictBadge: React.FC<VerdictBadgeProps> = ({ verdict, size = 'small' }) => {
  const getVerdictColor = (v: string) => {
    switch (v.toLowerCase()) {
      case 'allow': return COLORS.allow;
      case 'deny': return COLORS.deny;
      case 'degrade': return COLORS.degrade;
      default: return '#9E9E9E';
    }
  };

  const color = getVerdictColor(verdict);

  return (
    <Chip
      label={verdict.toUpperCase()}
      size={size}
      sx={{
        bgcolor: `${color}20`,
        color: color,
        fontWeight: 'bold',
        borderRadius: 1,
      }}
    />
  );
};

export default VerdictBadge;
