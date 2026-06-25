import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function Home() {
  const session = cookies().get('admin_session')?.value;
  redirect(session ? '/dashboard' : '/login');
}
