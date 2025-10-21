import type { Metadata } from 'next';
import './admin.css';

import AdminSidebar from '@/components/admin/AdminSidebar';

export const metadata: Metadata = {
  title: '管理ダッシュボード | 旅ログまっぷ',
};

export default function ManageLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="admin-container">
      <AdminSidebar />
      <section className="admin-main">{children}</section>
    </div>
  );
}
