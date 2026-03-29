import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  CircularProgress,
  Alert,
} from '@mui/material';
import { packApi } from '@/lib/api';
import PackCard from '@/components/PackCard';

export default function PacksPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [qualityTier, setQualityTier] = useState('');
  const perPage = 12;

  const { data, isLoading, error } = useQuery({
    queryKey: ['packs', page, search, category, qualityTier],
    queryFn: () =>
      packApi.listPacks({
        page,
        per_page: perPage,
        search: search || undefined,
        category: category || undefined,
        quality_tier: qualityTier || undefined,
      }),
  });

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Browse Texture Packs
      </Typography>

      <Box sx={{ mb: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Search"
          variant="outlined"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          sx={{ minWidth: 300 }}
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={category}
            label="Category"
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="PBR">PBR</MenuItem>
            <MenuItem value="Stylized">Stylized</MenuItem>
            <MenuItem value="UI">UI</MenuItem>
            <MenuItem value="Environment">Environment</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Quality Tier</InputLabel>
          <Select
            value={qualityTier}
            label="Quality Tier"
            onChange={(e) => {
              setQualityTier(e.target.value);
              setPage(1);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="pixel">Pixel</MenuItem>
            <MenuItem value="standard">Standard</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="cinematic">Cinematic</MenuItem>
            <MenuItem value="ultra">Ultra</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          Failed to load texture packs. Please try again.
        </Alert>
      )}

      {data && data.data.length === 0 && (
        <Alert severity="info">
          No texture packs found matching your criteria.
        </Alert>
      )}

      {data && data.data.length > 0 && (
        <>
          <Grid container spacing={3}>
            {data.data.map((pack) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={pack.id}>
                <PackCard pack={pack} />
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
            <Pagination
              count={data.pagination.total_pages}
              page={page}
              onChange={handlePageChange}
              color="primary"
              size="large"
            />
          </Box>
        </>
      )}
    </Box>
  );
}
