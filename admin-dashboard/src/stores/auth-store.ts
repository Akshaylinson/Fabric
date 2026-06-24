import { create } from 'zustand';
import type { Role } from '@/types';

type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: Role;
};

type AuthState = {
  token: string | null;
  user: AuthUser | null;
  login: (user: AuthUser, token: string) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null })
}));

