/**
 * Backend status indicator component
 */

'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/lib/store';

export default function StatusIndicator() {
  const { backendStatus, checkBackendStatus } = useAppStore();

  useEffect(() => {
    // Check status on mount
    checkBackendStatus();

    // Set up polling every 5 seconds
    const interval = setInterval(() => {
      checkBackendStatus();
    }, 5000);

    return () => clearInterval(interval);
  }, [checkBackendStatus]);

  const getStatusColor = () => {
    switch (backendStatus) {
      case 'online':
        return 'var(--accent)';
      case 'offline':
        return 'var(--error)';
      default:
        return 'var(--primary)';
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'online':
        return 'Backend Online';
      case 'offline':
        return 'Backend Offline';
      default:
        return 'Checking...';
    }
  };

  return (
    <div
      className="mb-6 p-3 rounded-lg text-center text-sm font-mono"
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: `1px solid ${getStatusColor()}`,
        color: getStatusColor(),
      }}
    >
      <div className="flex items-center justify-center gap-2">
        <div
          className="w-2 h-2 rounded-full"
          style={{
            background: getStatusColor(),
            animation: backendStatus === 'checking' ? 'pulse 2s infinite' : 'none',
          }}
        />
        {getStatusText()}
      </div>
    </div>
  );
}
