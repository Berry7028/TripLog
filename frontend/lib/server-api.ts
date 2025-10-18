import { buildApiUrl } from './config';

import type {
  AuthStatusResponse,
  HomeResponse,
  MySpotsResponse,
  ProfileResponse,
  RankingResponse,
  SpotsResponse,
  SpotDetailResponse,
} from '@/types/api';

type QueryParams = Record<string, string | string[] | undefined>;

function buildQueryString(params: QueryParams = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((v) => qs.append(key, v));
    } else if (value !== undefined) {
      qs.set(key, value);
    }
  });
  const str = qs.toString();
  return str ? `?${str}` : '';
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(buildApiUrl(path), { cache: 'no-store' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function fetchHomeSpots(params: QueryParams = {}): Promise<HomeResponse> {
  const qs = buildQueryString(params);
  return getJson<HomeResponse>(`/api/home/${qs}`);
}

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  return getJson<AuthStatusResponse>('/api/auth/me/');
}

export async function fetchMySpots(): Promise<MySpotsResponse> {
  return getJson<MySpotsResponse>('/api/my-spots/');
}

export async function fetchSpotDetail(spotId: number): Promise<SpotDetailResponse> {
  return getJson<SpotDetailResponse>(`/api/spots/${spotId}/detail/`);
}

export async function fetchProfile(): Promise<ProfileResponse> {
  return getJson<ProfileResponse>('/api/profile/');
}

export async function fetchRecentSpots(): Promise<SpotsResponse> {
  return getJson<SpotsResponse>('/api/recent-spots/');
}

export async function fetchRanking(): Promise<RankingResponse> {
  return getJson<RankingResponse>('/api/ranking/');
}

export async function fetchSpotsByFilter(params: QueryParams = {}): Promise<SpotsResponse> {
  const qs = buildQueryString(params);
  return getJson<SpotsResponse>(`/api/spots/${qs}`);
}


