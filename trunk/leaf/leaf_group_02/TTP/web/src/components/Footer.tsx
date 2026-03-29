import { Box, Container, Typography, Link } from '@mui/material';

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.background.paper,
      }}
    >
      <Container maxWidth="xl">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' TTP - Texture Pack Repository. '}
          <Link color="inherit" href="https://github.com/ttp/ttp">
            GitHub
          </Link>
        </Typography>
      </Container>
    </Box>
  );
}
