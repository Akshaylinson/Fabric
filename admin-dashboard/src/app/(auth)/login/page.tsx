import Link from 'next/link';
import { Card } from '@/components/ui';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md space-y-6 border-cyan-400/20 bg-slate-950/70">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300/80">Admin Access</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Textile AI Control Panel</h1>
          <p className="mt-2 text-sm text-slate-300">Sign in to inspect workflows, health, logs, and AI jobs.</p>
        </div>
        <form className="space-y-4">
          <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Email" />
          <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Password" type="password" />
          <button className="w-full rounded-2xl bg-cyan-400 px-4 py-3 font-semibold text-slate-950">Login</button>
        </form>
        <div className="flex items-center justify-between text-sm text-slate-300">
          <Link href="/forgot-password" className="hover:text-cyan-300">
            Forgot password
          </Link>
          <span>JWT + RBAC ready</span>
        </div>
      </Card>
    </div>
  );
}

