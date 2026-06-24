import { Card, Pill, SectionTitle, TableShell } from '@/components/ui';
import { monitoringServices } from '@/services/mock-data';

export default function MonitoringPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Live Ops" title="Platform Monitoring" description="Track service health, uptime, response time, and health checks in one place." />
      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3">Service</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Uptime</th>
              <th className="px-4 py-3">Response Time</th>
              <th className="px-4 py-3">Health Check</th>
            </tr>
          </thead>
          <tbody>
            {monitoringServices.map((service) => (
              <tr key={service.name} className="border-t border-white/10">
                <td className="px-4 py-3 text-white">{service.name}</td>
                <td className="px-4 py-3">
                  <Pill tone={service.status === 'Healthy' ? 'success' : service.status === 'Warning' ? 'warning' : 'danger'}>{service.status}</Pill>
                </td>
                <td className="px-4 py-3">{service.uptime}</td>
                <td className="px-4 py-3">{service.responseTime}</td>
                <td className="px-4 py-3">/health</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableShell>
      <Card>
        <h3 className="font-semibold text-white">Service Map</h3>
        <p className="mt-2 text-sm text-slate-300">Gateway, Auth, Business, Orchestrator, Template, Fabric, Try-On, PostgreSQL, Redis, and MinIO are all represented here.</p>
      </Card>
    </div>
  );
}

