import { Card, SectionTitle } from '@/components/ui';

const workflowCards = [
  {
    title: 'Workflow 1 - Garment Template Creation',
    description: 'Upload front, back, and side images, then inspect template package JSON, masks, metadata, and processing logs.'
  },
  {
    title: 'Workflow 2 - Fabric Mapping',
    description: 'Choose a template, upload a fabric image, generate a render, and compare version outputs with timing data.'
  },
  {
    title: 'Workflow 3 - Virtual Try-On',
    description: 'Upload a customer photo and rendered garment, then generate a preview with response payload and job details.'
  }
];

export default function WorkflowTestingPage() {
  return (
    <div className="space-y-6">
      <SectionTitle
        eyebrow="Testing Console"
        title="AI Workflow Testing"
        description="This is the primary QA surface for validating every AI pipeline with request/response visibility."
      />
      <div className="grid gap-4 xl:grid-cols-3">
        {workflowCards.map((card) => (
          <Card key={card.title}>
            <h3 className="text-lg font-semibold text-white">{card.title}</h3>
            <p className="mt-2 text-sm text-slate-300">{card.description}</p>
            <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">
              Workflow-specific upload form, action buttons, raw request/response view, and processing logs go here.
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

