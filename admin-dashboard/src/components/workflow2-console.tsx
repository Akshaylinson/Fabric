'use client';

import { ChangeEvent, useEffect, useMemo, useState } from 'react';

import { Card, Pill, SectionTitle } from '@/components/ui';
import { useAuthStore } from '@/stores/auth-store';
import {
  listWorkflow2Templates,
  renderWorkflow2Garment,
  type Workflow2ImageSelection,
  type Workflow2RenderRequest,
  type Workflow2RenderResponse,
  type Workflow2TemplateSummary
} from '@/services/workflow2';

function createEmptySelection(placeholder: string): Workflow2ImageSelection {
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

function FabricUploadCard({
  selection,
  onChange
}: {
  selection: Workflow2ImageSelection;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className="block rounded-3xl border border-dashed border-white/15 bg-slate-950/60 p-4 transition hover:border-cyan-400/40 hover:bg-white/[0.04]">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-white">Fabric image</div>
          <div className="mt-1 text-xs text-slate-400">Upload the customer-selected fabric for the render.</div>
        </div>
        <Pill tone={selection.preview ? 'success' : 'neutral'}>{selection.preview ? 'Uploaded' : 'Pending'}</Pill>
      </div>
      <div className="mt-4 flex items-center gap-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-white/5 text-xs text-slate-400">
          {selection.preview ? <img src={selection.preview} alt="Fabric preview" className="h-full w-full object-cover" /> : 'Preview'}
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

export function Workflow2Console() {
  const token = useAuthStore((state) => state.token);
  const [fabricImage, setFabricImage] = useState(createEmptySelection('fabric_selection_ref.png'));
  const [templates, setTemplates] = useState<Workflow2TemplateSummary[]>([]);
  const [templateRef, setTemplateRef] = useState('');
  const [renderLabel, setRenderLabel] = useState('Workflow 2 - Fabric Render');
  const [comparisonRenderRef, setComparisonRenderRef] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);
  const [statusMessage, setStatusMessage] = useState('Ready to map a fabric onto a selected template.');
  const [error, setError] = useState<string | null>(null);
  const [requestPayload, setRequestPayload] = useState<Workflow2RenderRequest | null>(null);
  const [result, setResult] = useState<Workflow2RenderResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadTemplates() {
      setIsLoadingTemplates(true);
      try {
        const response = await listWorkflow2Templates({ token });
        if (cancelled) {
          return;
        }
        setTemplates(response.items);
        setTemplateRef((current) => current || response.items[0]?.template_id || '');
        setStatusMessage(response.items.length ? 'Templates loaded from the template service.' : 'No templates found yet. Create one in Workflow 1 first.');
      } catch (cause) {
        if (!cancelled) {
          const message = cause instanceof Error ? cause.message : 'Unable to load templates.';
          setError(message);
          setStatusMessage('Unable to load live templates.');
        }
      } finally {
        if (!cancelled) {
          setIsLoadingTemplates(false);
        }
      }
    }

    void loadTemplates();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const selectedTemplate = useMemo(
    () => templates.find((item) => item.template_id === templateRef) ?? templates[0] ?? null,
    [templateRef, templates]
  );

  async function updateSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      setFabricImage(createEmptySelection('fabric_selection_ref.png'));
      return;
    }

    const preview = await readFileAsDataUrl(file);
    setFabricImage({
      ref: file.name,
      preview,
      fileName: file.name,
      fileSizeLabel: `${(file.size / 1024 / 1024).toFixed(2)} MB`
    });
  }

  function buildPayload(compareAgainstCurrent = false): Workflow2RenderRequest {
    return {
      fabric_ref: fabricImage.ref,
      template_ref: templateRef.trim() || selectedTemplate?.template_id || 'tpl_001',
      fabric_image_data: fabricImage.preview || undefined,
      render_label: renderLabel.trim() || 'Workflow 2 Fabric Render',
      comparison_render_ref: compareAgainstCurrent ? result?.render_id ?? undefined : comparisonRenderRef.trim() || undefined
    };
  }

  async function handleGenerateRender(compareAgainstCurrent = false) {
    const payload = buildPayload(compareAgainstCurrent);
    setIsSubmitting(true);
    setError(null);
    setRequestPayload(payload);
    setStatusMessage(compareAgainstCurrent ? 'Generating a comparison render...' : 'Submitting Workflow 2 render request...');

    try {
      const response = await renderWorkflow2Garment(payload, { token });
      setResult(response);
      setStatusMessage(
        response.comparison
          ? `Render ${response.render_id} completed with version comparison.`
          : `Render ${response.render_id} completed successfully.`
      );
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Unable to generate render.';
      setError(message);
      setStatusMessage('Workflow 2 request failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const outputRender = result?.rendered_image_ref ?? 'Rendered garment preview will appear here.';

  return (
    <Card className="space-y-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <SectionTitle
          eyebrow="Testing Console"
          title="Workflow 2 - Fabric Mapping"
          description="Select a live template, upload fabric, generate a render, compare versions, and inspect the full mock payloads and logs."
        />
        <div className="flex flex-wrap gap-2">
          <Pill tone={result ? 'success' : 'neutral'}>{result ? 'Render ready' : 'Awaiting render'}</Pill>
          <Pill tone={isSubmitting ? 'warning' : 'neutral'}>{isSubmitting ? 'Processing' : isLoadingTemplates ? 'Loading templates' : 'Idle'}</Pill>
          <Pill>QA mode</Pill>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Input Capture</h3>
              <p className="mt-1 text-sm text-slate-300">Stage the fabric and template used by the fabric service.</p>
            </div>
            <Pill tone="neutral">Workflow 2</Pill>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 md:col-span-2">
              <span className="text-sm text-slate-300">Template</span>
              <select
                value={templateRef}
                onChange={(event) => setTemplateRef(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-400/40"
              >
                <option value="" className="bg-slate-950 text-white">Select a template</option>
                {templates.map((template) => (
                  <option key={template.template_id} value={template.template_id} className="bg-slate-950 text-white">
                    {template.template_id} - {template.template_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="space-y-2">
              <span className="text-sm text-slate-300">Render label</span>
              <input
                value={renderLabel}
                onChange={(event) => setRenderLabel(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="Workflow 2 - Fabric Render"
              />
            </label>
            <label className="space-y-2">
              <span className="text-sm text-slate-300">Compare against render ref</span>
              <input
                value={comparisonRenderRef}
                onChange={(event) => setComparisonRenderRef(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="Optional: render ref to compare versions"
              />
            </label>
          </div>

          <FabricUploadCard selection={fabricImage} onChange={(event) => void updateSelection(event)} />

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSubmitting || !templateRef}
              onClick={() => void handleGenerateRender()}
              className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Generate Render
            </button>
            <button
              type="button"
              disabled={isSubmitting || !result}
              onClick={() => void handleGenerateRender(true)}
              className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Compare Versions
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
            {!templates.length && !isLoadingTemplates ? <div className="mt-3 text-sm text-amber-200">Create a Workflow 1 template first so this console can load it from the backend.</div> : null}
          </div>
        </Card>

        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Live Output</h3>
              <p className="mt-1 text-sm text-slate-300">Inspect the render response and version comparison details returned by the fabric service.</p>
            </div>
            <Pill tone={result ? 'success' : 'neutral'}>{result ? result.version_label : 'No result yet'}</Pill>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Generated Garment</div>
              <div className="mt-3 flex min-h-56 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-slate-950/70 p-4">
                <div className="space-y-2 text-center">
                  <div className="text-xs uppercase tracking-[0.28em] text-cyan-300/80">Preview</div>
                  <div className="text-sm font-medium text-white">{selectedTemplate?.template_name ?? 'Template pending'}</div>
                  <p className="max-w-xs text-xs leading-6 text-slate-400">{outputRender}</p>
                </div>
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Render Summary</div>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                <div className="flex items-center justify-between gap-3">
                  <span>Render ID</span>
                  <span className="text-white">{result?.render_id ?? 'Pending'}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Template</span>
                  <span className="text-white">{result?.template_ref ?? templateRef}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Fabric</span>
                  <span className="text-white">{result?.fabric_ref ?? fabricImage.ref}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Processing time</span>
                  <span className="text-white">{result ? `${result.timing.processing_time_ms} ms` : '0 ms'}</span>
                </div>
              </div>
              {result?.comparison ? (
                <div className="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                  {result.comparison.summary}
                </div>
              ) : null}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
            <div className="text-sm font-semibold text-white">Metadata</div>
            <pre className="mt-3 overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">
              {result ? formatJson(result.metadata) : 'Metadata appears after a render.'}
            </pre>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Request</h3>
            <p className="mt-1 text-sm text-slate-300">The exact request payload sent to the fabric service through the dashboard proxy route.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">
            {requestPayload ? formatJson(requestPayload) : 'No request has been sent yet.'}
          </pre>
        </Card>

        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Response</h3>
            <p className="mt-1 text-sm text-slate-300">The mock render response returned by the backend, including logs, timing, and version history.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">
            {result ? formatJson(result) : 'No response available yet.'}
          </pre>
        </Card>
      </div>

      <Card className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Processing Logs</h3>
          <p className="mt-1 text-sm text-slate-300">A compact timeline for debugging Workflow 2 mapping steps and version comparisons.</p>
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
          {!result ? <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">Logs will appear once a render is generated.</div> : null}
        </div>
      </Card>

      <Card className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Version History</h3>
          <p className="mt-1 text-sm text-slate-300">Use the compare mode to keep multiple render versions visible in the same test session.</p>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {(result?.version_history ?? []).map((entry) => (
            <div key={`${entry.version}-${entry.render_ref}`} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-white">{entry.version}</span>
                <Pill tone="neutral">{entry.label}</Pill>
              </div>
              <p className="mt-3 break-all text-xs text-slate-400">{entry.render_ref}</p>
            </div>
          ))}
          {!result ? <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">Version history will appear after the first render.</div> : null}
        </div>
      </Card>
    </Card>
  );
}
