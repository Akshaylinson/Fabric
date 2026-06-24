'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';
import { useUiStore } from '@/stores/ui-store';

export function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient());
  const darkMode = useUiStore((state) => state.darkMode);

  return (
    <QueryClientProvider client={client}>
      <div className={darkMode ? 'dark' : ''}>{children}</div>
    </QueryClientProvider>
  );
}

