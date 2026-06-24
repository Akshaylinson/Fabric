import { Card, SectionTitle } from '@/components/ui';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Reports" title="Analytics" description="Usage, workflow, storage, and user analytics designed for internal review." />
      <div className="grid gap-4 xl:grid-cols-2">
        <Card><h3 className="font-semibold text-white">Usage Analytics</h3><p className="mt-2 text-sm text-slate-300">Jobs per day, jobs per month, and active users charts.</p></Card>
        <Card><h3 className="font-semibold text-white">Workflow Analytics</h3><p className="mt-2 text-sm text-slate-300">Success rate by workflow, average duration, and failure trends.</p></Card>
        <Card><h3 className="font-semibold text-white">Storage Analytics</h3><p className="mt-2 text-sm text-slate-300">Storage growth and image generation trends.</p></Card>
        <Card><h3 className="font-semibold text-white">User Analytics</h3><p className="mt-2 text-sm text-slate-300">Most active users and most used templates.</p></Card>
      </div>
    </div>
  );
}

