import { cn } from '@/utils/cn';
import type { ReactNode } from 'react';

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('rounded-3xl border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur', className)}>{children}</div>;
}

export function SectionTitle({ eyebrow, title, description }: { eyebrow?: string; title: string; description?: string }) {
  return (
    <div className="space-y-1">
      {eyebrow ? <p className="text-xs uppercase tracking-[0.28em] text-cyan-300/80">{eyebrow}</p> : null}
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      {description ? <p className="max-w-3xl text-sm text-slate-300">{description}</p> : null}
    </div>
  );
}

export function MetricCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-emerald-500/10" />
      <div className="relative">
        <p className="text-sm text-slate-300">{label}</p>
        <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
        {hint ? <p className="mt-2 text-xs text-slate-400">{hint}</p> : null}
      </div>
    </Card>
  );
}

export function Pill({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'success' | 'warning' | 'danger' }) {
  const toneClass =
    tone === 'success'
      ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/20'
      : tone === 'warning'
        ? 'bg-amber-500/15 text-amber-300 border-amber-500/20'
        : tone === 'danger'
          ? 'bg-rose-500/15 text-rose-300 border-rose-500/20'
          : 'bg-white/10 text-slate-200 border-white/10';
  return <span className={cn('inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium', toneClass)}>{children}</span>;
}

export function TableShell({ children }: { children: ReactNode }) {
  return <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-950/60">{children}</div>;
}

