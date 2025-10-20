'use client';

import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';

import { ensureCsrfToken } from '@/lib/csrf';

interface FavoriteButtonProps {
  spotId: number;
  initialFavorite: boolean;
  disabled?: boolean;
}

export default function FavoriteButton({ spotId, initialFavorite, disabled }: FavoriteButtonProps) {
  const router = useRouter();
  const [isFavorite, setIsFavorite] = useState(initialFavorite);
  const [isPending, startTransition] = useTransition();

  const toggleFavorite = () => {
    startTransition(async () => {
      const token = await ensureCsrfToken();
      if (!token) {
        console.error('CSRF token is unavailable; cannot update favorites.');
        return;
      }

      const response = await fetch(`/api/spots/${spotId}/favorite`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
        },
      });
      if (response.ok) {
        const json = await response.json();
        if (typeof json.is_favorite === 'boolean') {
          setIsFavorite(json.is_favorite);
        }
        router.refresh();
      }
    });
  };

  return (
    <button
      type="button"
      onClick={toggleFavorite}
      disabled={disabled || isPending}
      className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
        isFavorite ? 'bg-rose-500 text-white hover:bg-rose-600' : 'bg-white text-rose-500 hover:bg-rose-50'
      } border border-rose-400`}
    >
      {isFavorite ? 'お気に入り済み' : 'お気に入りに追加'}
    </button>
  );
}
