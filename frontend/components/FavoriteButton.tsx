'use client';

import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';

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
      const response = await fetch(`/api/spots/${spotId}/favorite`, {
        method: 'POST',
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
