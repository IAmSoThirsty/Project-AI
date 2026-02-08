/**
 * Environment variable validation and typing
 */

import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url().default('http://localhost:5000'),
  NEXT_PUBLIC_API_TIMEOUT: z.string().transform(Number).default('30000'),
  NEXT_PUBLIC_APP_NAME: z.string().default('Project-AI'),
  NEXT_PUBLIC_APP_VERSION: z.string().default('1.0.0'),
  NEXT_PUBLIC_ENV: z.enum(['development', 'production', 'test']).default('production'),
});

export type Env = z.infer<typeof envSchema>;

let env: Env;

try {
  env = envSchema.parse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_API_TIMEOUT: process.env.NEXT_PUBLIC_API_TIMEOUT,
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
    NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION,
    NEXT_PUBLIC_ENV: process.env.NEXT_PUBLIC_ENV,
  });
} catch (error) {
  if (error instanceof z.ZodError) {
    console.error('Environment validation failed:', error.errors);
  }
  throw new Error('Invalid environment configuration');
}

export { env };
