import { Card, Pill, SectionTitle, TableShell } from '@/components/ui';
import { templates } from '@/services/mock-data';

export default function TemplatesPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Management" title="Template Library" description="Search, filter, edit metadata, reprocess, and inspect full template histories." />
      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3">Template ID</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Created By</th>
              <th className="px-4 py-3">Created Date</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {templates.map((item) => (
              <tr key={item.id} className="border-t border-white/10">
                <td className="px-4 py-3 text-white">{item.id}</td>
                <td className="px-4 py-3">{item.name}</td>
                <td className="px-4 py-3">{item.type}</td>
                <td className="px-4 py-3">{item.createdBy}</td>
                <td className="px-4 py-3">{item.createdDate}</td>
                <td className="px-4 py-3">
                  <Pill tone={item.status === 'Active' ? 'success' : 'neutral'}>{item.status}</Pill>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableShell>
      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <h3 className="font-semibold text-white">Template Detail</h3>
          <p className="mt-2 text-sm text-slate-300">Images, metadata, masks, AI description, and processing history are surfaced here.</p>
        </Card>
        <Card>
          <h3 className="font-semibold text-white">Reprocess Action</h3>
          <p className="mt-2 text-sm text-slate-300">Trigger a new analysis pass with the current AI adapters.</p>
        </Card>
        <Card>
          <h3 className="font-semibold text-white">Versioning</h3>
          <p className="mt-2 text-sm text-slate-300">Compare preview generations and keep template lifecycle context visible.</p>
        </Card>
      </div>
    </div>
  );
}

