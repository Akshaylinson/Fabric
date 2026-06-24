import Link from 'next/link';
import { Card } from '@/components/ui';

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md space-y-6">
        <h1 className="text-2xl font-semibold text-white">Reset Password</h1>
        <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="New password" type="password" />
        <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Confirm password" type="password" />
        <button className="w-full rounded-2xl bg-cyan-400 px-4 py-3 font-semibold text-slate-950">Reset Password</button>
        <Link href="/login" className="text-sm text-cyan-300">
          Return to login
        </Link>
      </Card>
    </div>
  );
}

