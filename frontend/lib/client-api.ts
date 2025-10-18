'use client';

import { buildApiUrl } from './config';
import { buildQueryString, type QueryParams } from './api-helpers';

async function getJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    ...init,
    credentials: 'include',
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchAuthStatus() {
  return getJson<any>('/api/auth/me/');
}

export async function fetchSpotsByFilter(params: QueryParams = {}) {
  const qs = buildQueryString(params);
  return getJson<any>(`/api/spots/${qs}`);
}
