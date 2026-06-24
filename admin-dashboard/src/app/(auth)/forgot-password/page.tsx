import Link from 'next/link';
import { Card } from '@/components/ui';

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md space-y-6">
        <h1 className="text-2xl font-semibold text-white">Forgot Password</h1>
        <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Email" />
        <button className="w-full rounded-2xl bg-emerald-400 px-4 py-3 font-semibold text-slate-950">Send Reset Link</button>
        <Link href="/login" className="text-sm text-cyan-300">
          Back to login
        </Link>
      </Card>
    </div>
  );
}

