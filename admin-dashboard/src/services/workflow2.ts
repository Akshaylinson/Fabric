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
  render_label?: string;
  comparison_render_ref?: string;
};

export type Workflow2RenderResponse = {
  render_id: string;
  render_label: string;
  status: string;
  template_ref: string;
  fabric_ref: string;
  rendered_image_ref: string;
  version_label: string;
  metadata: {
    preserved_structure: boolean;
    fabric_fit: string;
    texture_strategy: string;
    garment_area_covered: string;
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
