import { getBaseUrl } from '@/services/api';

const fabricServiceBaseUrl = getBaseUrl('fabric');

export async function GET(_request: Request, { params }: { params: { renderId: string } }) {
  const response = await fetch(`${fabricServiceBaseUrl}/renders/${params.renderId}/image`, {
    method: 'GET',
    cache: 'no-store'
  });

  if (!response.ok) {
    const message = await response.text();
    return new Response(message || 'Render image not found', { status: response.status });
  }

  const headers = new Headers();
  const contentType = response.headers.get('content-type');
  if (contentType) {
    headers.set('content-type', contentType);
  }
  headers.set('cache-control', 'no-store');

  return new Response(response.body, {
    status: response.status,
    headers
  });
}
