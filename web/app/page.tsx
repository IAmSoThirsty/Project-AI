/**
 * Home/Login page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import LoginForm from '@/components/LoginForm';
import StatusIndicator from '@/components/StatusIndicator';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && isAuthenticated && !isLoading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, mounted, router]);

  if (!mounted) {
    return null;
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="card">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold mb-2" style={{ color: 'var(--primary)' }}>
              Project-AI
            </h1>
            <p className="text-gray-400">Production-Grade AI Assistant</p>
          </div>

          <StatusIndicator />

          <LoginForm />

          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Demo credentials:</p>
            <p>admin / open-sesame</p>
            <p>guest / letmein</p>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Built with Next.js 14 · TypeScript · Zustand</p>
          <p className="mt-2">© 2026 Project-AI Team</p>
        </div>
      </div>
    </main>
  );
}
