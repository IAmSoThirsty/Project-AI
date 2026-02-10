/**
 * Root layout for Next.js application
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../styles/globals.css';
import { env } from '@/lib/env';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: `${env.NEXT_PUBLIC_APP_NAME} - AI Assistant`,
  description: 'Production-grade AI assistant with ethical decision-making and autonomous learning',
  keywords: ['AI', 'Assistant', 'Machine Learning', 'PyQt6', 'Desktop Application'],
  authors: [{ name: 'Project AI Team' }],
  robots: 'index, follow',
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#060510',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
