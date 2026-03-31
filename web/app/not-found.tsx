/**
 * 404 Not Found page
 */

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="card max-w-md w-full text-center">
        <h2 className="text-6xl font-bold mb-4" style={{ color: 'var(--primary)' }}>
          404
        </h2>
        <p className="text-xl text-gray-400 mb-6">
          Page not found
        </p>
        <Link href="/" className="button button-primary inline-block">
          Go Home
        </Link>
      </div>
    </div>
  );
}
