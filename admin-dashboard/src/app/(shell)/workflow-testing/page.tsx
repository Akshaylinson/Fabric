'use client';

import { ChangeEvent, useState } from 'react';

import { Card, Pill, SectionTitle } from '@/components/ui';
import { useAuthStore } from '@/stores/auth-store';
import { Workflow2Console } from '@/components/workflow2-console';
import {
  createWorkflow1Template,
  reanalyzeWorkflow1Template,
  type Workflow1ImageSelection,
  type Workflow1TemplateRequest,
  type Workflow1TemplateResponse
} from '@/services/workflow1';

type ViewMode = 'package' | 'metadata' | 'masks';

function createEmptySelection(placeholder: string): Workflow1ImageSelection {
  return {
    ref: placeholder,
    preview: '',
    fileName: placeholder,
    fileSizeLabel: 'Awaiting upload'
  };
}

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function readFileAsDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.onerror = () => reject(new Error(`Unable to read ${file.name}`));
    reader.readAsDataURL(file);
  });
}

function ImageUploadCard({
  label,
  description,
  selection,
  onChange
}: {
  label: string;
  description: string;
  selection: Workflow1ImageSelection;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className="block rounded-3xl border border-dashed border-white/15 bg-slate-950/60 p-4 transition hover:border-cyan-400/40 hover:bg-white/[0.04]">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-white">{label}</div>
          <div className="mt-1 text-xs text-slate-400">{description}</div>
        </div>
        <Pill tone={selection.preview ? 'success' : 'neutral'}>{selection.preview ? 'Uploaded' : 'Pending'}</Pill>
      </div>
      <div className="mt-4 flex items-center gap-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-white/5 text-xs text-slate-400">
          {selection.preview ? <img src={selection.preview} alt={label} className="h-full w-full object-cover" /> : 'Preview'}
        </div>
        <div className="min-w-0 flex-1 space-y-2">
          <input type="file" accept="image/*" className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-cyan-400/15 file:px-4 file:py-2 file:text-cyan-100 file:transition hover:file:bg-cyan-400/25" onChange={onChange} />
          <div className="truncate text-xs text-slate-400">Ref: {selection.ref}</div>
          <div className="text-xs text-slate-500">{selection.fileName}</div>
          <div className="text-xs text-slate-500">{selection.fileSizeLabel}</div>
        </div>
      </div>
    </label>
  );
}

export default function WorkflowTestingPage() {
  const token = useAuthStore((state) => state.token);
  const [frontImage, setFrontImage] = useState(createEmptySelection('front_design_ref.png'));
  const [backImage, setBackImage] = useState(createEmptySelection('back_design_ref.png'));
  const [sideImage, setSideImage] = useState(createEmptySelection('side_design_ref.png'));
  const [templateName, setTemplateName] = useState('Workflow 1 - Tailored Shirt');
  const [creatorId, setCreatorId] = useState('designer_042');
  const [creatorName, setCreatorName] = useState('Asha Kumar');
  const [rerunReason, setRerunReason] = useState('Manual QA rerun');
  const [selectedView, setSelectedView] = useState<ViewMode>('package');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Ready to create a new template package.');
  const [error, setError] = useState<string | null>(null);
  const [requestPayload, setRequestPayload] = useState<Workflow1TemplateRequest | null>(null);
  const [result, setResult] = useState<Workflow1TemplateResponse | null>(null);

  const imageSelections = [
    {
      label: 'Front image',
      description: 'Primary garment view used for template extraction.',
      selection: frontImage,
      placeholder: 'front_design_ref.png',
      update: setFrontImage
    },
    {
      label: 'Back image',
      description: 'Rear garment view for structural validation.',
      selection: backImage,
      placeholder: 'back_design_ref.png',
      update: setBackImage
    },
    {
      label: 'Side image',
      description: 'Profile garment view for silhouette accuracy.',
      selection: sideImage,
      placeholder: 'side_design_ref.png',
      update: setSideImage
    }
  ] as const;

  async function updateSelection(
    setter: (next: Workflow1ImageSelection) => void,
    placeholder: string,
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];
    if (!file) {
      setter(createEmptySelection(placeholder));
      return;
    }

    const preview = await readFileAsDataUrl(file);
    setter({
      ref: file.name,
      preview,
      fileName: file.name,
      fileSizeLabel: `${(file.size / 1024 / 1024).toFixed(2)} MB`
    });
  }

  function buildPayload(): Workflow1TemplateRequest {
    return {
      template_name: templateName.trim() || 'Workflow 1 Template',
      front_image_ref: frontImage.ref,
      back_image_ref: backImage.ref,
      side_image_ref: sideImage.ref,
      front_image_data: frontImage.preview || undefined,
      back_image_data: backImage.preview || undefined,
      side_image_data: sideImage.preview || undefined,
      image_refs: [frontImage.ref, backImage.ref, sideImage.ref],
      creator_id: creatorId.trim() || 'designer_042',
      creator_name: creatorName.trim() || 'Asha Kumar'
    };
  }

  async function handleCreateTemplate() {
    const payload = buildPayload();
    setIsSubmitting(true);
    setError(null);
    setRequestPayload(payload);
    setStatusMessage('Submitting Workflow 1 template creation request...');

    try {
      const response = await createWorkflow1Template(payload, { token });
      setResult(response);
      setSelectedView('package');
      setStatusMessage(`Template ${response.template_id} created with analysis version ${response.analysis_version}.`);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Unable to create template.';
      setError(message);
      setStatusMessage('Workflow 1 request failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleReanalyze() {
    if (!result) {
      setStatusMessage('Create a template before re-running analysis.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setStatusMessage(`Re-running analysis for ${result.template_id}...`);

    try {
      const response = await reanalyzeWorkflow1Template(result.template_id, { reason: rerunReason.trim() || 'Manual QA rerun' }, { token });
      setResult(response);
      setSelectedView('package');
      setStatusMessage(`Template ${response.template_id} re-analyzed at version ${response.analysis_version}.`);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Unable to rerun analysis.';
      setError(message);
      setStatusMessage('Workflow 1 re-analysis failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const outputTemplate = result?.template_package ?? result;
  const displayMetadata = result?.metadata ?? null;
  const displayMasks = result?.segmentation_masks ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <SectionTitle
          eyebrow="Testing Console"
          title="Workflow 1 - Garment Template Creation"
          description="Upload front, back, and side garment images, create a reusable template package, rerun analysis, and inspect the raw API payloads."
        />
        <div className="flex flex-wrap gap-2">
          <Pill tone={result ? 'success' : 'neutral'}>{result ? 'Template ready' : 'Awaiting creation'}</Pill>
          <Pill tone={isSubmitting ? 'warning' : 'neutral'}>{isSubmitting ? 'Processing' : 'Idle'}</Pill>
          <Pill>QA mode</Pill>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Input Capture</h3>
              <p className="mt-1 text-sm text-slate-300">Stage the garment views and metadata used by the mock template service.</p>
            </div>
            <Pill tone="neutral">Workflow 1</Pill>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm text-slate-300">Template name</span>
              <input
                value={templateName}
                onChange={(event) => setTemplateName(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="Workflow 1 - Tailored Shirt"
              />
            </label>
            <label className="space-y-2">
              <span className="text-sm text-slate-300">Creator ID</span>
              <input
                value={creatorId}
                onChange={(event) => setCreatorId(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="designer_042"
              />
            </label>
            <label className="space-y-2 md:col-span-2">
              <span className="text-sm text-slate-300">Creator name</span>
              <input
                value={creatorName}
                onChange={(event) => setCreatorName(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="Asha Kumar"
              />
            </label>
            <label className="space-y-2 md:col-span-2">
              <span className="text-sm text-slate-300">Re-run analysis note</span>
              <input
                value={rerunReason}
                onChange={(event) => setRerunReason(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="Manual QA rerun"
              />
            </label>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            {imageSelections.map((item) => (
              <ImageUploadCard
                key={item.label}
                label={item.label}
                description={item.description}
                selection={item.selection}
                onChange={(event) => void updateSelection(item.update, item.placeholder, event)}
              />
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => void handleCreateTemplate()}
              className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Create Template
            </button>
            <button
              type="button"
              disabled={isSubmitting || !result}
              onClick={() => void handleReanalyze()}
              className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Re-run Analysis
            </button>
            <button
              type="button"
              onClick={() => setSelectedView('metadata')}
              className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              View Metadata
            </button>
            <button
              type="button"
              onClick={() => setSelectedView('masks')}
              className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              View Segmentation Masks
            </button>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-sm font-semibold text-white">Status</div>
                <div className="mt-1 text-sm text-slate-300">{statusMessage}</div>
              </div>
              <Pill tone={error ? 'danger' : 'success'}>{error ? 'Needs attention' : 'Connected'}</Pill>
            </div>
            {error ? <div className="mt-3 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
          </div>
        </Card>

        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Live Output</h3>
              <p className="mt-1 text-sm text-slate-300">Preview the template package that the backend mock generates for workflow validation.</p>
            </div>
            <Pill tone={result ? 'success' : 'neutral'}>{result ? `v${result.analysis_version}` : 'No result yet'}</Pill>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            {[
              { label: 'Front', item: frontImage },
              { label: 'Back', item: backImage },
              { label: 'Side', item: sideImage }
            ].map(({ label, item }) => (
              <div key={label} className="overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                <div className="aspect-square bg-slate-950/70">
                  {item.preview ? <img src={item.preview} alt={label} className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center text-sm text-slate-500">No preview</div>}
                </div>
                <div className="border-t border-white/10 px-3 py-2">
                  <div className="text-sm font-medium text-white">{label}</div>
                  <div className="truncate text-xs text-slate-400">{item.fileName}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Template Summary</div>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                <div className="flex items-center justify-between gap-3">
                  <span>Template ID</span>
                  <span className="text-white">{result?.template_id ?? 'Pending'}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Name</span>
                  <span className="text-white">{result?.template_name ?? templateName}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Creator</span>
                  <span className="text-white">{result ? `${result.creator.name} (${result.creator.id})` : creatorName}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Analysis version</span>
                  <span className="text-white">{result?.analysis_version ?? 0}</span>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">View Mode</div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button type="button" onClick={() => setSelectedView('package')} className={`rounded-full px-4 py-2 text-sm transition ${selectedView === 'package' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-white hover:bg-white/10'}`}>
                  Package JSON
                </button>
                <button type="button" onClick={() => setSelectedView('metadata')} className={`rounded-full px-4 py-2 text-sm transition ${selectedView === 'metadata' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-white hover:bg-white/10'}`}>
                  Metadata
                </button>
                <button type="button" onClick={() => setSelectedView('masks')} className={`rounded-full px-4 py-2 text-sm transition ${selectedView === 'masks' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-white hover:bg-white/10'}`}>
                  Masks
                </button>
              </div>
              <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
                {selectedView === 'metadata' ? (
                  <pre className="overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">{displayMetadata ? formatJson(displayMetadata) : 'Metadata will appear after template creation.'}</pre>
                ) : selectedView === 'masks' ? (
                  <div className="space-y-2">
                    {displayMasks.length ? displayMasks.map((mask) => <div key={mask} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-slate-200">{mask}</div>) : <p className="text-slate-400">Segmentation masks will appear after template creation.</p>}
                  </div>
                ) : (
                  <pre className="overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">{outputTemplate ? formatJson(outputTemplate) : 'Template package JSON will appear after creation.'}</pre>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Request</h3>
            <p className="mt-1 text-sm text-slate-300">The exact request payload sent to the template service through the dashboard proxy route.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">
            {requestPayload ? formatJson(requestPayload) : 'No request has been sent yet.'}
          </pre>
        </Card>

        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Response</h3>
            <p className="mt-1 text-sm text-slate-300">The mock template package returned by the backend, including masks, metadata, logs, and version history.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">
            {result ? formatJson(result) : 'No response available yet.'}
          </pre>
        </Card>
      </div>

      <Card className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Processing Logs</h3>
          <p className="mt-1 text-sm text-slate-300">A compact timeline for debugging Workflow 1 analysis steps and reruns.</p>
        </div>
        <div className="grid gap-3 lg:grid-cols-2 xl:grid-cols-4">
          {(result?.processing_logs ?? []).map((entry) => (
            <div key={`${entry.timestamp}-${entry.stage}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between gap-2">
                <div className="text-sm font-semibold text-white">{entry.stage}</div>
                <Pill tone="neutral">{entry.timestamp.slice(11, 19)}</Pill>
              </div>
              <p className="mt-3 text-sm text-slate-300">{entry.message}</p>
            </div>
          ))}
          {!result ? <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">Logs will appear once a template is created.</div> : null}
        </div>
      </Card>
      <Workflow2Console />
    </div>
  );
}
