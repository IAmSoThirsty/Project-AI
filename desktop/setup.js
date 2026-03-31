//                                           [2026-03-03 13:45]
//                                          Productivity: Active
#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Project AI Desktop - Setup Script\n');

// Check if Node.js version is compatible
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));

if (majorVersion < 18) {
  console.error('❌ Error: Node.js 18 or higher is required.');
  console.error(`   Current version: ${nodeVersion}`);
  process.exit(1);
}

console.log('✅ Node.js version check passed');

// Check if package.json exists
if (!fs.existsSync('package.json')) {
  console.error('❌ Error: package.json not found. Run this script from the desktop directory.');
  process.exit(1);
}

// Install dependencies
console.log('\n📦 Installing dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('✅ Dependencies installed successfully');
} catch (error) {
  console.error('❌ Failed to install dependencies');
  process.exit(1);
}

// Create .env file if it doesn't exist
if (!fs.existsSync('.env')) {
  console.log('\n📝 Creating .env file...');
  if (fs.existsSync('.env.example')) {
    fs.copyFileSync('.env.example', '.env');
    console.log('✅ .env file created from .env.example');
  }
}

// Check if backend is running
console.log('\n🔍 Checking Governance Kernel...');
const http = require('http');
const options = {
  hostname: 'localhost',
  port: 8001,
  path: '/health',
  method: 'GET',
  timeout: 3000
};

const req = http.request(options, (res) => {
  if (res.statusCode === 200) {
    console.log('✅ Governance Kernel is running at http://localhost:8001');
    console.log('\n✨ Setup complete! You can now run:');
    console.log('   npm run dev     - Start development server');
    console.log('   npm run build   - Build for production');
    console.log('   npm start       - Run production build\n');
  }
});

req.on('error', () => {
  console.log('⚠️  Governance Kernel is not running');
  console.log('   Start it with: cd .. && python start_api.py');
  console.log('\n✨ Setup complete! You can now run:');
  console.log('   npm run dev     - Start development server');
  console.log('   npm run build   - Build for production');
  console.log('   npm start       - Run production build\n');
});

req.on('timeout', () => {
  req.destroy();
});

req.end();
