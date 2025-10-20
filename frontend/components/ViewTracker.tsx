'use client';

import { useEffect } from 'react';

import { ensureCsrfToken } from '@/lib/csrf';

interface ViewTrackerProps {
  spotId: number;
  enabled: boolean;
}

export default function ViewTracker({ spotId, enabled }: ViewTrackerProps) {
  useEffect(() => {
    if (!enabled) {
      return () => {};
    }
    const start = performance.now();

    return () => {
      const duration = performance.now() - start;
      (async () => {
        const token = await ensureCsrfToken();
        if (!token) {
          console.error('CSRF token is unavailable; cannot record view duration.');
          return;
        }

        fetch(`/api/spots/${spotId}/record-view`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token,
          },
          body: JSON.stringify({ duration_ms: duration }),
          keepalive: true,
        }).catch((error) => console.error('Failed to record view duration', error));
      })();
    };
  }, [spotId, enabled]);

  return null;
}
