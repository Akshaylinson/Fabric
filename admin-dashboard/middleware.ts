import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

const authRoutes = ['/login', '/forgot-password', '/reset-password'];
const protectedRoutes = [
  '/dashboard',
  '/workflow-testing',
  '/templates',
  '/jobs',
  '/assets',
  '/users',
  '/analytics',
  '/monitoring',
  '/logs',
  '/api-explorer',
  '/settings'
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  const session = request.cookies.get('admin_session')?.value;
  const isAuthRoute = authRoutes.includes(pathname);
  const isProtectedRoute = protectedRoutes.some((route) => pathname === route || pathname.startsWith(`${route}/`));

  if (session && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  if (!session && isProtectedRoute) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
};
