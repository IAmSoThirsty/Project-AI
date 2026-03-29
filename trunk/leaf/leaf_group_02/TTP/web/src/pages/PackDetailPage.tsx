import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Button,
  Chip,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Download,
  ArrowBack,
  Info,
  Category,
  Label,
} from '@mui/icons-material';
import { packApi } from '@/lib/api';
import toast from 'react-hot-toast';

export default function PackDetailPage() {
  const { packId } = useParams<{ packId: string }>();
  const navigate = useNavigate();

  const { data: pack, isLoading, error } = useQuery({
    queryKey: ['pack', packId],
    queryFn: () => packApi.getPack(packId!),
    enabled: !!packId,
  });

  const handleDownload = () => {
    toast.success('Download started!');
    // In production, this would trigger actual download
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !pack) {
    return (
      <Alert severity="error">
        Failed to load texture pack. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/packs')}
        sx={{ mb: 3 }}
      >
        Back to Packs
      </Button>

      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Card>
            <Box
              component="img"
              src={pack.preview_image_url || '/placeholder-texture.jpg'}
              alt={pack.name}
              sx={{ width: '100%', height: 400, objectFit: 'cover' }}
            />
            <CardContent>
              <Typography variant="h4" gutterBottom>
                {pack.name}
              </Typography>
              <Typography variant="body1" paragraph color="text.secondary">
                {pack.description}
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
                <Chip label={pack.quality_tier} color="primary" />
                <Chip label={pack.category} variant="outlined" />
                <Chip label={`v${pack.version}`} variant="outlined" />
                <Chip label={pack.license} variant="outlined" icon={<Info />} />
              </Box>

              <Divider sx={{ my: 3 }} />

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Label /> Tags
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {pack.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" />
                  ))}
                </Box>
              </Box>

              {pack.author && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Author
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {pack.author.username}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<Download />}
                onClick={handleDownload}
                sx={{ mb: 3 }}
              >
                Download Pack
              </Button>

              <Typography variant="h6" gutterBottom>
                Pack Information
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Size
                  </Typography>
                  <Typography variant="body1">
                    {(pack.size_bytes / (1024 * 1024)).toFixed(2)} MB
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Downloads
                  </Typography>
                  <Typography variant="body1">
                    {pack.download_count.toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Typography variant="body1">
                    {pack.status}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Updated
                  </Typography>
                  <Typography variant="body1">
                    {new Date(pack.updated_at).toLocaleDateString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {new Date(pack.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
