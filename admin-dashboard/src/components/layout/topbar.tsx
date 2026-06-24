'use client';

import { Bell, MoonStar, Search, Menu } from 'lucide-react';
import { useUiStore } from '@/stores/ui-store';
import { useAuthStore } from '@/stores/auth-store';
import { Pill } from '@/components/ui';

export function Topbar() {
  const toggleSidebar = useUiStore((state) => state.toggleSidebar);
  const toggleTheme = useUiStore((state) => state.toggleTheme);
  const user = useAuthStore((state) => state.user);

  return (
    <header className="flex items-center gap-3 border-b border-white/10 bg-slate-950/60 px-4 py-4 backdrop-blur xl:px-6">
      <button className="rounded-2xl border border-white/10 bg-white/5 p-2 text-slate-200 xl:hidden" onClick={toggleSidebar} aria-label="Open menu">
        <Menu className="h-5 w-5" />
      </button>
      <div className="flex flex-1 items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <Search className="h-4 w-4 text-slate-400" />
        <input
          className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
          placeholder="Search templates, jobs, users, logs..."
        />
      </div>
      <button className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-200" onClick={toggleTheme} aria-label="Toggle theme">
        <MoonStar className="h-4 w-4" />
      </button>
      <button className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-200" aria-label="Notifications">
        <Bell className="h-4 w-4" />
      </button>
      <div className="hidden items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 md:flex">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-emerald-400 text-sm font-semibold text-slate-950">
          {user?.name?.slice(0, 1) ?? 'A'}
        </div>
        <div>
          <div className="text-sm font-medium text-white">{user?.name ?? 'Admin User'}</div>
          <div className="text-xs text-slate-400">{user?.role ?? 'Super Admin'}</div>
        </div>
        <Pill tone="success">Online</Pill>
      </div>
    </header>
  );
}

