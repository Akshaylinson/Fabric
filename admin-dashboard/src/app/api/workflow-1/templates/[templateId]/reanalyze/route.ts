import { NextResponse } from 'next/server';

import { getBaseUrl } from '@/services/api';

const templateServiceBaseUrl = getBaseUrl('template');

export async function POST(request: Request, { params }: { params: { templateId: string } }) {
  const { templateId } = params;
  const body = await request.json();
  const response = await fetch(`${templateServiceBaseUrl}/templates/${templateId}/reanalyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body),
    cache: 'no-store'
  });

  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
