export type Workflow3ImageSelection = {
  ref: string;
  preview: string;
  fileName: string;
  fileSizeLabel: string;
};

export type Workflow3ProcessingLog = {
  timestamp: string;
  stage: string;
  message: string;
};

export type Workflow3TryOnRequest = {
  customer_image_ref: string;
  render_id: string;
  customer_image_data?: string;
};

export type Workflow3TryOnResponse = {
  job_id: string | null;
  preview_id: string;
  render_id: string;
  customer_source_ref: string;
  garment_source_ref: string | null;
  output_image_ref: string;
  image_url: string;
  provider: string;
  model: string;
  model_version: string | null;
  prompt: string;
  customer_validation: {
    valid: boolean;
    reason: string;
  };
  garment_validation: {
    valid: boolean;
    reason: string;
  };
  quality_validation: {
    valid: boolean;
    reason: string;
  };
  notes: string;
  timing: {
    started_at: string;
    completed_at: string;
    processing_time_ms: number;
  };
  processing_logs: Workflow3ProcessingLog[];
  face_preserved: boolean;
  body_shape_preserved: boolean;
  garment_structure_preserved: boolean;
  fabric_appearance_preserved: boolean;
};

type Workflow3RequestOptions = {
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

export async function renderWorkflow3Preview(
  payload: Workflow3TryOnRequest,
  options: Workflow3RequestOptions = {}
): Promise<Workflow3TryOnResponse> {
  const response = await fetch('/api/workflow-3/render', {
    method: 'POST',
    headers: buildHeaders(options.token),
    body: JSON.stringify(payload),
    cache: 'no-store'
  });

  return parseResponse<Workflow3TryOnResponse>(response);
}
