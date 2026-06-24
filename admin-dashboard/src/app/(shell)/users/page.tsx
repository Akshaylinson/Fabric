import { Card, Pill, SectionTitle, TableShell } from '@/components/ui';
import { users } from '@/services/mock-data';

export default function UsersPage() {
  return (
    <div className="space-y-6">
      <SectionTitle eyebrow="Identity" title="User Management" description="Create, edit, disable, assign roles, and reset passwords for internal users." />
      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Last Login</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.email} className="border-t border-white/10">
                <td className="px-4 py-3 text-white">{user.name}</td>
                <td className="px-4 py-3">{user.email}</td>
                <td className="px-4 py-3">{user.role}</td>
                <td className="px-4 py-3">
                  <Pill tone={user.status === 'Active' ? 'success' : 'danger'}>{user.status}</Pill>
                </td>
                <td className="px-4 py-3">{user.lastLogin}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableShell>
      <div className="grid gap-4 xl:grid-cols-3">
        <Card><h3 className="font-semibold text-white">Create User</h3><p className="mt-2 text-sm text-slate-300">Invite new staff from the admin panel.</p></Card>
        <Card><h3 className="font-semibold text-white">Assign Role</h3><p className="mt-2 text-sm text-slate-300">Super Admin, Admin, AI Engineer, Developer, QA Engineer.</p></Card>
        <Card><h3 className="font-semibold text-white">Reset Password</h3><p className="mt-2 text-sm text-slate-300">JWT-backed auth flows stay connected to Auth Service APIs.</p></Card>
      </div>
    </div>
  );
}

