'use client';

import { useRouter } from 'next/navigation';
import { useTransition } from 'react';

export default function LogoutButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const handleLogout = () => {
    startTransition(async () => {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
      });
      if (response.ok) {
        router.push('/');
        router.refresh();
      }
    });
  };

  return (
    <button
      type="button"
      onClick={handleLogout}
      disabled={isPending}
      className="text-white hover:text-gray-200 transition"
      title="ログアウト"
    >
      <i className="fa-solid fa-right-from-bracket" style={{ color: '#F5BABB' }}></i>
    </button>
  );
}
