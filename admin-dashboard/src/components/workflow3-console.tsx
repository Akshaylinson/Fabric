'use client';

import { ChangeEvent, useMemo, useState } from 'react';

import { Card, Pill, SectionTitle } from '@/components/ui';
import { useAuthStore } from '@/stores/auth-store';
import { renderWorkflow3Preview, type Workflow3ImageSelection, type Workflow3TryOnRequest, type Workflow3TryOnResponse } from '@/services/workflow3';

function createEmptySelection(placeholder: string): Workflow3ImageSelection {
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

export function Workflow3Console() {
  const token = useAuthStore((state) => state.token);
  const [customerImage, setCustomerImage] = useState(createEmptySelection('customer_photo_ref.png'));
  const [renderId, setRenderId] = useState('rnd_000');
  const [statusMessage, setStatusMessage] = useState('Ready to pair a customer photo with a Workflow 2 garment render.');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [requestPayload, setRequestPayload] = useState<Workflow3TryOnRequest | null>(null);
  const [result, setResult] = useState<Workflow3TryOnResponse | null>(null);

  const garmentPreviewUrl = useMemo(() => {
    const trimmed = renderId.trim();
    return trimmed ? `/api/workflow-2/renders/${trimmed}/image` : null;
  }, [renderId]);

  async function updateSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      setCustomerImage(createEmptySelection('customer_photo_ref.png'));
      return;
    }

    const preview = await readFileAsDataUrl(file);
    setCustomerImage({
      ref: file.name,
      preview,
      fileName: file.name,
      fileSizeLabel: `${(file.size / 1024 / 1024).toFixed(2)} MB`
    });
  }

  function buildPayload(): Workflow3TryOnRequest {
    return {
      customer_image_ref: customerImage.ref,
      render_id: renderId.trim() || 'rnd_000',
      customer_image_data: customerImage.preview || undefined
    };
  }

  async function handleGeneratePreview() {
    const payload = buildPayload();
    setIsSubmitting(true);
    setError(null);
    setRequestPayload(payload);
    setStatusMessage('Submitting Workflow 3 try-on request...');

    try {
      const response = await renderWorkflow3Preview(payload, { token });
      setResult(response);
      setStatusMessage(`Preview ${response.preview_id} generated successfully via ${response.provider}.`);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Unable to generate try-on preview.';
      setError(message);
      setStatusMessage('Workflow 3 request failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const previewImageUrl = result?.image_url ?? (result ? `/api/workflow-3/renders/${result.preview_id}/image` : null);

  return (
    <Card className="space-y-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <SectionTitle
          eyebrow="Testing Console"
          title="Workflow 3 - Customer Try-On"
          description="Upload a customer photo, point the workflow at a Workflow 2 garment render, generate an API-driven preview, and inspect the full provider response."
        />
        <div className="flex flex-wrap gap-2">
          <Pill tone={result ? 'success' : 'neutral'}>{result ? 'Preview ready' : 'Awaiting preview'}</Pill>
          <Pill tone={isSubmitting ? 'warning' : 'neutral'}>{isSubmitting ? 'Processing' : 'Idle'}</Pill>
          <Pill>QA mode</Pill>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-white">Input Capture</h3>
              <p className="mt-1 text-sm text-slate-300">Stage the customer image and Workflow 2 render ID used to generate the try-on preview.</p>
            </div>
            <Pill tone="neutral">Workflow 3</Pill>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 md:col-span-2">
              <span className="text-sm text-slate-300">Workflow 2 render ID</span>
              <input
                value={renderId}
                onChange={(event) => setRenderId(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
                placeholder="rnd_000"
              />
            </label>
          </div>

          <label className="block rounded-3xl border border-dashed border-white/15 bg-slate-950/60 p-4 transition hover:border-cyan-400/40 hover:bg-white/[0.04]">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-white">Customer image</div>
                <div className="mt-1 text-xs text-slate-400">Upload the customer photo that should be matched to the garment render.</div>
              </div>
              <Pill tone={customerImage.preview ? 'success' : 'neutral'}>{customerImage.preview ? 'Uploaded' : 'Pending'}</Pill>
            </div>
            <div className="mt-4 flex items-center gap-4">
              <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-white/5 text-xs text-slate-400">
                {customerImage.preview ? <img src={customerImage.preview} alt="Customer preview" className="h-full w-full object-cover" /> : 'Preview'}
              </div>
              <div className="min-w-0 flex-1 space-y-2">
                <input type="file" accept="image/*" className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-cyan-400/15 file:px-4 file:py-2 file:text-cyan-100 file:transition hover:file:bg-cyan-400/25" onChange={updateSelection} />
                <div className="truncate text-xs text-slate-400">Ref: {customerImage.ref}</div>
                <div className="text-xs text-slate-500">{customerImage.fileName}</div>
                <div className="text-xs text-slate-500">{customerImage.fileSizeLabel}</div>
              </div>
            </div>
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSubmitting || !renderId.trim()}
              onClick={() => void handleGeneratePreview()}
              className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Generate Try-On Preview
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
              <p className="mt-1 text-sm text-slate-300">Inspect the try-on preview and the provider metadata returned by the try-on service.</p>
            </div>
            <Pill tone={result ? 'success' : 'neutral'}>{result ? result.provider : 'No result yet'}</Pill>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Generated Preview</div>
              <div className="mt-3 flex min-h-56 items-center justify-center overflow-hidden rounded-2xl border border-dashed border-white/10 bg-slate-950/70 p-2">
                {previewImageUrl ? (
                  <img
                    src={previewImageUrl}
                    alt={result?.preview_id || 'Workflow 3 generated preview'}
                    className="h-full w-full rounded-xl object-cover"
                  />
                ) : (
                  <div className="space-y-2 text-center">
                    <div className="text-xs uppercase tracking-[0.28em] text-cyan-300/80">Preview</div>
                    <div className="text-sm font-medium text-white">Workflow 3 output</div>
                    <p className="max-w-xs text-xs leading-6 text-slate-400">The try-on image will appear here after a successful render.</p>
                  </div>
                )}
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Render Summary</div>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                <div className="flex items-center justify-between gap-3">
                  <span>Preview ID</span>
                  <span className="text-white">{result?.preview_id ?? 'Pending'}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Workflow 2 Render</span>
                  <span className="text-white">{result?.render_id ?? renderId}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Provider</span>
                  <span className="text-white">{result?.provider ?? 'Pending'}</span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span>Processing time</span>
                  <span className="text-white">{result ? `${result.timing.processing_time_ms} ms` : '0 ms'}</span>
                </div>
              </div>
              <div className="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {result?.notes ?? 'The preview will be validated and stored once generated.'}
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Customer Validation</div>
              <pre className="mt-3 overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">{result ? formatJson(result.customer_validation) : 'Validation appears after a preview is generated.'}</pre>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Garment Validation</div>
              <pre className="mt-3 overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">{result ? formatJson(result.garment_validation) : 'Validation appears after a preview is generated.'}</pre>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
            <div className="text-sm font-semibold text-white">Prompt</div>
            <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-200">{result ? result.prompt : 'The structured AI prompt appears after a preview is generated.'}</pre>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Workflow 2 Garment Preview</h3>
            <p className="mt-1 text-sm text-slate-300">This is the garment render referenced by Workflow 3.</p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70 p-2">
            {garmentPreviewUrl ? (
              <img src={garmentPreviewUrl} alt="Workflow 2 garment preview" className="h-full w-full rounded-xl object-cover" />
            ) : (
              <div className="flex min-h-64 items-center justify-center text-sm text-slate-400">Enter a render ID to preview the garment render.</div>
            )}
          </div>
        </Card>

        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Request</h3>
            <p className="mt-1 text-sm text-slate-300">The exact request payload sent to the try-on service through the dashboard proxy route.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">{requestPayload ? formatJson(requestPayload) : 'No request has been sent yet.'}</pre>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Raw API Response</h3>
            <p className="mt-1 text-sm text-slate-300">The preview response returned by the backend, including timing, validations, and processing logs.</p>
          </div>
          <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-xs leading-6 text-slate-200">{result ? formatJson(result) : 'No response available yet.'}</pre>
        </Card>

        <Card className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Processing Logs</h3>
            <p className="mt-1 text-sm text-slate-300">A compact timeline for debugging Workflow 3 validation, prompt generation, and preview generation steps.</p>
          </div>
          <div className="grid gap-3 lg:grid-cols-2">
            {(result?.processing_logs ?? []).map((entry) => (
              <div key={`${entry.timestamp}-${entry.stage}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-2">
                  <div className="text-sm font-semibold text-white">{entry.stage}</div>
                  <Pill tone="neutral">{entry.timestamp.slice(11, 19)}</Pill>
                </div>
                <p className="mt-3 text-sm text-slate-300">{entry.message}</p>
              </div>
            ))}
            {!result ? <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">Logs will appear once a preview is generated.</div> : null}
          </div>
        </Card>
      </div>
    </Card>
  );
}
