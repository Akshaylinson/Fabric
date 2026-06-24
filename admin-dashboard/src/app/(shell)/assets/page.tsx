import { Card, SectionTitle } from '@/components/ui';
import { assets } from '@/services/mock-data';

export default function AssetsPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Library" title="Generated Assets" description="Preview and manage customer images, fabrics, templates, renders, and try-on results." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {assets.map((asset) => (
          <Card key={asset.name}>
            <div className="aspect-[4/3] rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-500/10 via-white/5 to-emerald-500/10" />
            <div className="mt-4 flex items-start justify-between gap-4">
              <div>
                <h3 className="font-semibold text-white">{asset.name}</h3>
                <p className="text-sm text-slate-400">{asset.category}</p>
              </div>
              <span className="text-xs text-slate-400">{asset.size}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

