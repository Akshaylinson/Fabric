'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/utils/cn';
import { LayoutDashboard, ScanLine, Boxes, BriefcaseBusiness, GalleryHorizontalEnd, Users, ChartColumnBig, HeartPulse, ScrollText, Code2, Settings } from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/workflow-testing', label: 'Workflow Testing', icon: ScanLine },
  { href: '/templates', label: 'Templates', icon: Boxes },
  { href: '/jobs', label: 'Jobs', icon: BriefcaseBusiness },
  { href: '/assets', label: 'Assets', icon: GalleryHorizontalEnd },
  { href: '/users', label: 'Users', icon: Users },
  { href: '/analytics', label: 'Analytics', icon: ChartColumnBig },
  { href: '/monitoring', label: 'Monitoring', icon: HeartPulse },
  { href: '/logs', label: 'Logs', icon: ScrollText },
  { href: '/api-explorer', label: 'API Explorer', icon: Code2 },
  { href: '/settings', label: 'Settings', icon: Settings }
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden h-screen w-72 shrink-0 border-r border-white/10 bg-slate-950/80 px-4 py-5 backdrop-blur xl:block">
      <div className="mb-6 rounded-3xl border border-cyan-400/20 bg-gradient-to-br from-cyan-500/15 to-emerald-500/10 p-4">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Textile AI</p>
        <h1 className="mt-2 text-xl font-semibold text-white">Admin Console</h1>
        <p className="mt-2 text-sm text-slate-300">Internal QA, monitoring, and workflow control plane.</p>
      </div>
      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition',
                active ? 'bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-400/20' : 'text-slate-300 hover:bg-white/5 hover:text-white'
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

