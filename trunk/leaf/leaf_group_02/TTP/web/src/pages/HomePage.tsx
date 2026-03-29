import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  CloudDownload,
  Security,
  Speed,
  Texture,
} from '@mui/icons-material';

const features = [
  {
    icon: <Texture fontSize="large" />,
    title: 'High-Quality Textures',
    description: 'From pixel art to ultra-realistic 8K photogrammetry textures',
  },
  {
    icon: <CloudDownload fontSize="large" />,
    title: 'Fast Downloads',
    description: 'CDN-powered delivery with resume support and regional caching',
  },
  {
    icon: <Security fontSize="large" />,
    title: 'Secure & Validated',
    description: 'All packs validated and scanned for quality and security',
  },
  {
    icon: <Speed fontSize="large" />,
    title: 'Production Ready',
    description: 'Enterprise-grade infrastructure with 99.9% uptime SLA',
  },
];

export default function HomePage() {
  return (
    <Box>
      <Container maxWidth="lg">
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
          }}
        >
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 700 }}
          >
            Texture Pack Repository
          </Typography>
          <Typography
            variant="h5"
            color="text.secondary"
            paragraph
            sx={{ mb: 4 }}
          >
            Production-grade texture asset management for game developers,
            artists, and studios
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              component={RouterLink}
              to="/packs"
            >
              Browse Packs
            </Button>
            <Button
              variant="outlined"
              size="large"
              component={RouterLink}
              to="/register"
            >
              Get Started
            </Button>
          </Box>
        </Box>

        <Grid container spacing={4} sx={{ mt: 4, mb: 8 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h4" gutterBottom>
            Quality Tiers
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            From indie pixel art to AAA photorealistic assets
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3, flexWrap: 'wrap' }}>
            {['Pixel', 'Standard', 'High', 'Cinematic', 'Ultra'].map((tier) => (
              <Card key={tier} sx={{ minWidth: 140 }}>
                <CardContent>
                  <Typography variant="h6">{tier}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
