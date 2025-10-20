'use client';

import { useRouter } from 'next/navigation';
import { useTransition } from 'react';

interface LogoutButtonProps {
  className?: string;
}

export default function LogoutButton({ className }: LogoutButtonProps) {
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
      className={className ?? 'text-white hover:text-gray-200 transition'}
      title="ログアウト"
    >
      <i className="fa-solid fa-right-from-bracket" style={{ color: '#F5BABB' }}></i>
      <span className="visually-hidden">ログアウト</span>
    </button>
  );
}
