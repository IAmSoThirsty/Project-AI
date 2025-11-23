// Simple placeholder index file for Node.js project
import { config } from 'dotenv';

config();

console.log('Project-AI Node.js service initialized');

// Export a simple health check
export const healthCheck = () => ({
  status: 'ok',
  timestamp: new Date().toISOString(),
  version: '1.0.0',
});

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Health check:', healthCheck());
}
