import type {
  AuthStatusResponse,
  HomeResponse,
  MySpotsResponse,
  ProfileResponse,
  RankingResponse,
  SpotDetailResponse,
  SpotsResponse,
} from '@/types/api';

import { buildApiUrl } from './config';

const isServer = typeof window === 'undefined';

type SearchParams = Record<string, string | string[] | undefined>;

async function getCookieHeader(): Promise<string | undefined> {
  if (!isServer) {
    return undefined;
  }

  try {
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const serialized = cookieStore
      .getAll()
      .map((item) => `${item.name}=${item.value}`)
      .join('; ');
    return serialized.length > 0 ? serialized : undefined;
  } catch (error) {
    return undefined;
  }
}

async function fetchJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  const cookieHeader = await getCookieHeader();
  if (cookieHeader && !headers.has('Cookie')) {
    headers.set('Cookie', cookieHeader);
  }

  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers,
    credentials: 'include',
    cache: init.cache ?? 'no-store',
  });

  if (!response.ok) {
    const message = await response.text().catch(() => '');
    throw new Error(`API request failed: ${response.status} ${response.statusText} ${message}`.trim());
  }

  return response.json() as Promise<T>;
}

export async function fetchHomeSpots(searchParams: SearchParams = {}): Promise<HomeResponse> {
  const params = new URLSearchParams();
  Object.entries(searchParams).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined) {
          params.append(key, item);
        }
      });
    } else if (value !== undefined) {
      params.append(key, value);
    }
  });

  const query = params.toString();
  const path = query ? `/spots/api/home/?${query}` : '/spots/api/home/';
  return fetchJson<HomeResponse>(path);
}

export async function fetchRanking(): Promise<RankingResponse> {
  return fetchJson<RankingResponse>('/spots/api/ranking/');
}

export async function fetchRecentSpots(): Promise<SpotsResponse> {
  return fetchJson<SpotsResponse>('/spots/api/recent-spots/');
}

export async function fetchMySpots(): Promise<MySpotsResponse> {
  return fetchJson<MySpotsResponse>('/spots/api/my-spots/');
}

export async function fetchProfile(): Promise<ProfileResponse> {
  return fetchJson<ProfileResponse>('/spots/api/profile/');
}

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  return fetchJson<AuthStatusResponse>('/spots/api/auth/me/');
}

export async function fetchSpotDetail(spotId: string): Promise<SpotDetailResponse> {
  return fetchJson<SpotDetailResponse>(`/spots/api/spots/${spotId}/detail/`);
}
