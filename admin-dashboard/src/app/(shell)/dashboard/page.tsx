import { Card, MetricCard, Pill, SectionTitle } from '@/components/ui';
import { dashboardMetrics, activityFeed } from '@/services/mock-data';
import { JobsChart, StorageChart, WorkflowChart } from '@/components/charts';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <SectionTitle
          eyebrow="Overview"
          title="Internal Admin Dashboard"
          description="Monitor platform health, track AI workflows, and inspect recent activity from the operating console."
        />
        <div className="flex gap-2">
          <Pill tone="success">All systems nominal</Pill>
          <Pill>QA mode</Pill>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dashboardMetrics.system.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} />
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {dashboardMetrics.ai.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} />
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {dashboardMetrics.storage.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <WorkflowChart />
        <Card>
          <SectionTitle eyebrow="Activity" title="Recent Activity Feed" description="A live-style operational feed for QA and admins." />
          <div className="mt-5 space-y-4">
            {activityFeed.map((item) => (
              <div key={item.message} className="flex items-start justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <div>
                  <div className="font-medium text-white">{item.message}</div>
                  <div className="text-sm text-slate-400">{item.time}</div>
                </div>
                <Pill tone={item.level === 'error' ? 'danger' : item.level === 'success' ? 'success' : 'neutral'}>{item.level}</Pill>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <JobsChart />
        <StorageChart />
      </section>
    </div>
  );
}

