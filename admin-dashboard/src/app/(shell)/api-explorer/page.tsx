import { Card, SectionTitle } from '@/components/ui';

export default function ApiExplorerPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Developer Tooling" title="API Explorer" description="Browse Swagger docs, execute requests, and inspect responses without leaving the dashboard." />
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <h3 className="font-semibold text-white">Swagger Documentation</h3>
          <p className="mt-2 text-sm text-slate-300">Embed the backend OpenAPI specs here for live inspection and execution.</p>
        </Card>
        <Card>
          <h3 className="font-semibold text-white">Request Runner</h3>
          <p className="mt-2 text-sm text-slate-300">Choose a service, build a request, send it, and review the raw response payload.</p>
        </Card>
      </div>
    </div>
  );
}

