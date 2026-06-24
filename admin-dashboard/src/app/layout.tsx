import type { Metadata } from 'next';
import { ReactNode } from 'react';
import './globals.css';
import { QueryProvider } from '@/components/providers/query-provider';

export const metadata: Metadata = {
  title: 'Textile AI Admin Dashboard',
  description: 'Internal admin dashboard and AI workflow testing console'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}

