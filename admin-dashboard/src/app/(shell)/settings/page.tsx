import { Card, SectionTitle } from '@/components/ui';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Preferences" title="Settings" description="Dashboard configuration, theme mode, API endpoints, and workspace preferences." />
      <div className="grid gap-4 xl:grid-cols-3">
        <Card><h3 className="font-semibold text-white">Theme</h3><p className="mt-2 text-sm text-slate-300">Dark and light mode support with a custom design system.</p></Card>
        <Card><h3 className="font-semibold text-white">API Base URLs</h3><p className="mt-2 text-sm text-slate-300">Point the dashboard at local, staging, or production services.</p></Card>
        <Card><h3 className="font-semibold text-white">RBAC</h3><p className="mt-2 text-sm text-slate-300">Role gates for Super Admin, Admin, AI Engineer, Developer, and QA Engineer.</p></Card>
      </div>
    </div>
  );
}

