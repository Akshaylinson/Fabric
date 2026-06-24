import { Card, Pill, SectionTitle, TableShell } from '@/components/ui';
import { logs } from '@/services/mock-data';

export default function LogsPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Debug" title="Logs Explorer" description="Search and filter centralized logs by service and severity." />
      <Card className="flex gap-3">
        <input className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Search logs" />
        <input className="w-56 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Filter by service" />
        <input className="w-48 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" placeholder="Severity" />
      </Card>
      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3">Service</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((entry) => (
              <tr key={`${entry.timestamp}-${entry.service}`} className="border-t border-white/10">
                <td className="px-4 py-3 text-white">{entry.timestamp}</td>
                <td className="px-4 py-3">{entry.service}</td>
                <td className="px-4 py-3">
                  <Pill tone={entry.severity === 'Error' ? 'danger' : entry.severity === 'Warning' ? 'warning' : 'neutral'}>{entry.severity}</Pill>
                </td>
                <td className="px-4 py-3">{entry.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableShell>
    </div>
  );
}

