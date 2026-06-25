export type Workflow1ImageSelection = {
  ref: string;
  preview: string;
  fileName: string;
  fileSizeLabel: string;
};

export type Workflow1ProcessingLog = {
  timestamp: string;
  stage: string;
  message: string;
};

export type Workflow1TemplateRequest = {
  template_name: string;
  front_image_ref: string;
  back_image_ref: string;
  side_image_ref: string;
  image_refs: string[];
  creator_id: string;
  creator_name: string;
};

export type Workflow1TemplateResponse = {
  template_id: string;
  template_name: string;
  preview_image: string;
  source_image_refs: string[];
  segmentation_masks: string[];
  metadata: {
    garment_type: string;
    collar_type: string;
    sleeve_type: string;
    fit_type: string;
    length: string;
    description: string;
    source_image_count?: number;
    [key: string]: unknown;
  };
  description: string;
  embedding_vector: number[];
  created_at: string;
  updated_at: string;
  analysis_version: number;
  creator: {
    id: string;
    name: string;
  };
  processing_logs: Workflow1ProcessingLog[];
  template_package: Record<string, unknown>;
  analysis_history: Array<Record<string, unknown>>;
};

export type Workflow1ReanalyzeRequest = {
  reason?: string;
};

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function createWorkflow1Template(payload: Workflow1TemplateRequest): Promise<Workflow1TemplateResponse> {
  const response = await fetch('/api/workflow-1/templates', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload),
    cache: 'no-store'
  });

  return parseResponse<Workflow1TemplateResponse>(response);
}

export async function reanalyzeWorkflow1Template(
  templateId: string,
  payload: Workflow1ReanalyzeRequest
): Promise<Workflow1TemplateResponse> {
  const response = await fetch(`/api/workflow-1/templates/${templateId}/reanalyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload),
    cache: 'no-store'
  });

  return parseResponse<Workflow1TemplateResponse>(response);
}
