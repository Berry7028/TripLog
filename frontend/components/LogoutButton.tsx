'use client';

import { useRouter } from 'next/navigation';
import { useTransition } from 'react';

import { ensureCsrfToken } from '@/lib/csrf';

interface LogoutButtonProps {
  className?: string;
}

export default function LogoutButton({ className }: LogoutButtonProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const handleLogout = () => {
    startTransition(async () => {
      const token = await ensureCsrfToken();
      if (!token) {
        console.error('CSRF token is unavailable; cannot log out securely.');
        return;
      }

      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
        },
      });
      if (response.ok) {
        // 認証状態変更イベントを発火
        window.dispatchEvent(new Event('authStateChanged'));
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
