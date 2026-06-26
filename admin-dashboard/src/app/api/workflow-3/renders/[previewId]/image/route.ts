import { getBaseUrl } from '@/services/api';

const tryonServiceBaseUrl = getBaseUrl('tryon');

export async function GET(_request: Request, { params }: { params: { previewId: string } }) {
  const response = await fetch(`${tryonServiceBaseUrl}/tryon/render/${params.previewId}/image`, {
    method: 'GET',
    cache: 'no-store'
  });

  if (!response.ok) {
    const message = await response.text();
    return new Response(message || 'Try-on preview image not found', { status: response.status });
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
