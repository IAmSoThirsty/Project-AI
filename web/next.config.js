/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export configuration for GitHub Pages deployment
  output: 'export',
  
  // Workspace root configuration
  outputFileTracingRoot: require('path').join(__dirname),
  
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
  
  // Strict mode for better error detection
  reactStrictMode: true,
  
  // Note: Security headers don't work with static export
  // Deploy to a server with custom headers or use a reverse proxy
  
  // TypeScript configuration
  typescript: {
    // Type check during build
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration
  eslint: {
    // Run ESLint during build
    ignoreDuringBuilds: false,
  },
  
  // Trailing slash for better static hosting compatibility
  trailingSlash: true,
  
  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_APP_NAME: 'Project-AI',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },
};

module.exports = nextConfig;
