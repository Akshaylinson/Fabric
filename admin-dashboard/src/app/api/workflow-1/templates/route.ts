import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

import { getBaseUrl } from '@/services/api';

const templateServiceBaseUrl = getBaseUrl('template');

function ensureSession() {
  return cookies().get('admin_session')?.value;
}

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
  if (!ensureSession()) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  return proxyToTemplateService('/templates/from-images', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

export async function GET() {
  if (!ensureSession()) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  return proxyToTemplateService('/templates', {
    method: 'GET'
  });
}
