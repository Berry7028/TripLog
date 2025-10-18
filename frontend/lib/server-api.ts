'use server';

import { cookies } from 'next/headers';

import { buildApiUrl } from './config';
import { buildQueryString, type QueryParams } from './api-helpers';

async function getJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const cookieStore = cookies();
  const cookieHeader = cookieStore.toString();

  const headers = new Headers(init.headers);
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }

  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers,
    credentials: 'include',
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchHomeSpots(params: QueryParams = {}) {
  const qs = buildQueryString(params);
  return getJson<any>(`/api/home/${qs}`);
}

export async function fetchAuthStatus() {
  return getJson<any>('/api/auth/me/');
}

export async function fetchMySpots() {
  return getJson<any>('/api/my-spots/');
}

export async function fetchSpotDetail(spotId: number) {
  return getJson<any>(`/api/spots/${spotId}/detail/`);
}

export async function fetchProfile() {
  return getJson<any>('/api/profile/');
}

export async function fetchRecentSpots() {
  return getJson<any>('/api/recent-spots/');
}

export async function fetchRanking() {
  return getJson<any>('/api/ranking/');
}

export async function fetchSpotsByFilter(params: QueryParams = {}) {
  const qs = buildQueryString(params);
  return getJson<any>(`/api/spots/${qs}`);
}
