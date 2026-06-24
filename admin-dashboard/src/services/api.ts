export type ApiRequestInit = RequestInit & {
  token?: string | null;
};

const baseUrls = {
  gateway: process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:3000',
  auth: process.env.NEXT_PUBLIC_AUTH_URL ?? 'http://localhost:3001',
  business: process.env.NEXT_PUBLIC_BUSINESS_URL ?? 'http://localhost:3002',
  orchestrator: process.env.NEXT_PUBLIC_ORCHESTRATOR_URL ?? 'http://localhost:8000',
  template: process.env.NEXT_PUBLIC_TEMPLATE_URL ?? 'http://localhost:8001',
  fabric: process.env.NEXT_PUBLIC_FABRIC_URL ?? 'http://localhost:8002',
  tryon: process.env.NEXT_PUBLIC_TRYON_URL ?? 'http://localhost:8003'
};

export function getBaseUrl(service: keyof typeof baseUrls) {
  return baseUrls[service];
}

export async function apiFetch<T>(url: string, init: ApiRequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init.token ? { Authorization: `Bearer ${init.token}` } : {}),
      ...(init.headers ?? {})
    },
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

