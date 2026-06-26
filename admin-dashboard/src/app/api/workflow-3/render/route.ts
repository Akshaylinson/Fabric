import { NextResponse } from 'next/server';

import { getBaseUrl } from '@/services/api';

const tryonServiceBaseUrl = getBaseUrl('tryon');

function getBearerToken(request: Request) {
  const authorization = request.headers.get('authorization');
  const [scheme, token] = authorization?.split(' ') ?? [];
  return scheme?.toLowerCase() === 'bearer' && token ? token : null;
}

export async function POST(request: Request) {
  if (!getBearerToken(request)) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const response = await fetch(`${tryonServiceBaseUrl}/tryon/render`, {
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
