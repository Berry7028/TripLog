'use client';

function readCookie(name: string): string | null {
  if (typeof document === 'undefined') {
    return null;
  }

  const pairs = document.cookie ? document.cookie.split(';') : [];
  for (const pair of pairs) {
    const [rawKey, ...rawValue] = pair.trim().split('=');
    if (rawKey === name) {
      return decodeURIComponent(rawValue.join('='));
    }
  }
  return null;
}

/**
 * Ensures a CSRF token cookie exists and returns its current value.
 * When the token is missing it triggers the backend helper endpoint to
 * refresh the cookie, mirroring Django's expected double-submit flow.
 */
export async function ensureCsrfToken(): Promise<string | null> {
  const existing = readCookie('csrftoken');
  if (existing) {
    return existing;
  }

  try {
    await fetch('/api/auth/csrf', { credentials: 'include' });
  } catch (error) {
    console.error('Failed to refresh CSRF token', error);
    return null;
  }

  return readCookie('csrftoken');
}

export function requireCsrfTokenOrThrow(token: string | null): string {
  if (!token) {
    throw new Error('CSRF token is unavailable');
  }
  return token;
}
