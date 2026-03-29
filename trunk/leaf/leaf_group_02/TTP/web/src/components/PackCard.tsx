import { Link as RouterLink } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  Box,
  CardActionArea,
} from '@mui/material';
import { Download } from '@mui/icons-material';
import type { TexturePack } from '@/types';

interface PackCardProps {
  pack: TexturePack;
}

const qualityColors = {
  pixel: 'default',
  standard: 'primary',
  high: 'secondary',
  cinematic: 'warning',
  ultra: 'error',
} as const;

export default function PackCard({ pack }: PackCardProps) {
  return (
    <Card>
      <CardActionArea component={RouterLink} to={`/packs/${pack.id}`}>
        <CardMedia
          component="img"
          height="200"
          image={pack.preview_image_url || '/placeholder-texture.jpg'}
          alt={pack.name}
          sx={{ objectFit: 'cover' }}
        />
        <CardContent>
          <Typography gutterBottom variant="h6" component="div" noWrap>
            {pack.name}
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {pack.description}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip
              label={pack.quality_tier}
              size="small"
              color={qualityColors[pack.quality_tier]}
            />
            <Chip label={pack.category} size="small" variant="outlined" />
            <Chip label={`v${pack.version}`} size="small" variant="outlined" />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Download fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {pack.download_count.toLocaleString()} downloads
            </Typography>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
