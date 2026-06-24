import { Card, Pill, SectionTitle, TableShell } from '@/components/ui';
import { jobs } from '@/services/mock-data';

export default function JobsPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Operations" title="AI Job Management" description="Search, filter, retry, cancel, and inspect logs for all workflow executions." />
      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3">Job ID</th>
              <th className="px-4 py-3">Workflow</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created At</th>
              <th className="px-4 py-3">Duration</th>
              <th className="px-4 py-3">User</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} className="border-t border-white/10">
                <td className="px-4 py-3 text-white">{job.id}</td>
                <td className="px-4 py-3">{job.workflow}</td>
                <td className="px-4 py-3">
                  <Pill tone={job.status === 'Completed' ? 'success' : job.status === 'Failed' ? 'danger' : 'warning'}>{job.status}</Pill>
                </td>
                <td className="px-4 py-3">{job.createdAt}</td>
                <td className="px-4 py-3">{job.duration}</td>
                <td className="px-4 py-3">{job.user}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableShell>
      <div className="grid gap-4 xl:grid-cols-3">
        <Card><h3 className="font-semibold text-white">Retry Failed Job</h3><p className="mt-2 text-sm text-slate-300">Available from the selected job detail view.</p></Card>
        <Card><h3 className="font-semibold text-white">Cancel Running Job</h3><p className="mt-2 text-sm text-slate-300">Use with safeguards for active workflows.</p></Card>
        <Card><h3 className="font-semibold text-white">View Logs</h3><p className="mt-2 text-sm text-slate-300">Per-job log stream and timeline live here.</p></Card>
      </div>
    </div>
  );
}

