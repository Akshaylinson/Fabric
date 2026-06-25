import { NextResponse } from 'next/server';

const adminEmail = process.env.ADMIN_DASHBOARD_EMAIL ?? 'admin@gmail.com';
const adminPassword = process.env.ADMIN_DASHBOARD_PASSWORD ?? 'admin123';

export async function POST(request: Request) {
  const { email, password } = (await request.json()) as { email?: string; password?: string };

  if (email !== adminEmail || password !== adminPassword) {
    return NextResponse.json({ message: 'Invalid admin credentials' }, { status: 401 });
  }

  const token = Buffer.from(`${email}:${Date.now()}`).toString('base64url');
  const response = NextResponse.json(
    {
      token,
      user: {
        id: 'admin_001',
        name: 'Admin User',
        email: adminEmail,
        role: 'Super Admin'
      }
    },
    { status: 200 }
  );

  response.cookies.set({
    name: 'admin_session',
    value: token,
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 8
  });

  return response;
}
