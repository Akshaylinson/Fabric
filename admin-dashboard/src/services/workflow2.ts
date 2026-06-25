export type Workflow2ImageSelection = {
  ref: string;
  preview: string;
  fileName: string;
  fileSizeLabel: string;
};

export type Workflow2ProcessingLog = {
  timestamp: string;
  stage: string;
  message: string;
};

export type Workflow2RenderRequest = {
  fabric_ref: string;
  template_ref: string;
  fabric_image_data?: string;
  render_label?: string;
  comparison_render_ref?: string;
};

export type Workflow2TemplateSummary = {
  template_id: string;
  template_name: string;
  created_at: string;
  updated_at: string;
  analysis_version: number;
};

export type Workflow2RenderResponse = {
  render_id: string;
  render_label: string;
  status: string;
  template_ref: string;
  fabric_ref: string;
  rendered_image_url: string;
  rendered_image_ref: string;
  provider: string;
  model: string;
  version_label: string;
  reference_count: number;
  references?: Array<{
    label: string;
    source_ref: string;
  }>;
  metadata: {
    provider: string;
    model: string;
    output_format: string;
    references_used: number;
    reference_labels: string[];
    fabric_source_ref: string;
    template_preview_ref: string | null;
    quality_profile: string;
    image_size: {
      width: number;
      height: number;
    };
    [key: string]: unknown;
  };
  comparison: {
    base_render_ref: string;
    current_version: string;
    compared_version: string;
    summary: string;
  } | null;
  version_history: Array<{
    version: string;
    render_ref: string;
    label: string;
  }>;
  timing: {
    started_at: string;
    completed_at: string;
    processing_time_ms: number;
  };
  processing_logs: Workflow2ProcessingLog[];
  notes: string;
};

type Workflow2RequestOptions = {
  token?: string | null;
};

function buildHeaders(token?: string | null): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function listWorkflow2Templates(
  options: Workflow2RequestOptions = {}
): Promise<{ items: Workflow2TemplateSummary[] }> {
  const response = await fetch('/api/workflow-1/templates', {
    method: 'GET',
    headers: buildHeaders(options.token),
    cache: 'no-store'
  });

  return parseResponse<{ items: Workflow2TemplateSummary[] }>(response);
}

export async function renderWorkflow2Garment(
  payload: Workflow2RenderRequest,
  options: Workflow2RequestOptions = {}
): Promise<Workflow2RenderResponse> {
  const response = await fetch('/api/workflow-2/render', {
    method: 'POST',
    headers: buildHeaders(options.token),
    body: JSON.stringify(payload),
    cache: 'no-store'
  });

  return parseResponse<Workflow2RenderResponse>(response);
}
