/**
 * Loading component for Next.js application
 */

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="loading mx-auto mb-4" style={{ width: '3rem', height: '3rem' }}></div>
        <p className="text-gray-400">Loading...</p>
      </div>
    </div>
  );
}
