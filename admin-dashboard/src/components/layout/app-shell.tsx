'use client';

import type { ReactNode } from 'react';
import { Sidebar } from './sidebar';
import { Topbar } from './topbar';
import { useUiStore } from '@/stores/ui-store';
import { cn } from '@/utils/cn';

export function AppShell({ children }: { children: ReactNode }) {
  const sidebarOpen = useUiStore((state) => state.sidebarOpen);
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.16),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.14),_transparent_25%),linear-gradient(180deg,#020617_0%,#0f172a_100%)] text-white">
      <div className="flex min-h-screen">
        <div className={cn('fixed inset-y-0 left-0 z-40 w-72 xl:static xl:block', sidebarOpen ? 'block' : 'hidden')}>
          <Sidebar />
        </div>
        <div className="flex min-h-screen flex-1 flex-col">
          <Topbar />
          <main className="flex-1 px-4 py-6 md:px-6 xl:px-8">{children}</main>
        </div>
      </div>
    </div>
  );
}

