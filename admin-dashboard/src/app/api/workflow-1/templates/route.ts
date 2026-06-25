import { NextResponse } from 'next/server';

import { getBaseUrl } from '@/services/api';

const templateServiceBaseUrl = getBaseUrl('template');

async function proxyToTemplateService(path: string, init: RequestInit) {
  const response = await fetch(`${templateServiceBaseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers ?? {})
    },
    cache: 'no-store'
  });

  const body = await response.json();
  return NextResponse.json(body, { status: response.status });
}

export async function POST(request: Request) {
  const body = await request.json();
  return proxyToTemplateService('/templates/from-images', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

export async function GET() {
  return proxyToTemplateService('/templates', {
    method: 'GET'
  });
}
