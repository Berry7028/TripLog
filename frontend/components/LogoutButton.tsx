'use client';

import { useRouter } from 'next/navigation';
import { useTransition } from 'react';

interface LogoutButtonProps {
  className?: string;
  onLoggedOut?: () => void;
}

export default function LogoutButton({ className, onLoggedOut }: LogoutButtonProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const handleLogout = () => {
    startTransition(async () => {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
      });
      if (response.ok) {
        onLoggedOut?.();
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
      className={
        className ??
        'btn btn-link nav-link p-0 text-white d-flex align-items-center hover:text-white'
      }
      title="ログアウト"
    >
      <i className="fa-solid fa-right-from-bracket" style={{ color: '#F5BABB' }}></i>
    </button>
  );
}
