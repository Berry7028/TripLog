import type {
  AuthStatusResponse,
  HomeResponse,
  MySpotsResponse,
  ProfileResponse,
  RankingResponse,
  SpotDetailResponse,
  SpotsResponse,
  SpotFilter,
} from '@/types/api';

import { buildApiUrl } from './config';

async function buildRequestInit(init: RequestInit = {}): Promise<RequestInit> {
  const headers = new Headers(init.headers);
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  const isServer = typeof window === 'undefined';
  if (isServer) {
    const { cookies } = await import('next/headers');
    const cookieStore = cookies();
    const cookieHeader = cookieStore
      .getAll()
      .map((cookie) => `${cookie.name}=${cookie.value}`)
      .join('; ');
    if (cookieHeader) {
      headers.set('Cookie', cookieHeader);
    }
  }

  const requestInit: RequestInit = {
    ...init,
    headers,
  };

  if (isServer) {
    requestInit.cache = init.cache ?? 'no-store';
    requestInit.credentials = init.credentials ?? 'include';
  } else {
    requestInit.credentials = init.credentials ?? 'include';
  }

  return requestInit;
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const finalInit = await buildRequestInit(init);
  const response = await fetch(buildApiUrl(path), finalInit);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function fetchHomeSpots(
  searchParams: Record<string, string | string[] | undefined>,
): Promise<HomeResponse> {
  const params = new URLSearchParams();
  Object.entries(searchParams).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => params.append(key, item));
    } else if (value !== undefined) {
      params.set(key, value);
    }
  });
  const query = params.toString();
  try {
    return await requestJson<HomeResponse>(`/spots/api/home/${query ? `?${query}` : ''}`);
  } catch (error) {
    return {
      spots: [],
      pagination: {
        page: 1,
        pages: 1,
        has_next: false,
        has_previous: false,
        total_count: 0,
      },
      search_query: '',
      sort_mode: 'recent',
      recommendation_notice: null,
      recommendation_source: null,
      recommendation_scored_ids: [],
    };
  }
}

export async function fetchSpotDetail(spotId: number): Promise<SpotDetailResponse> {
  return requestJson<SpotDetailResponse>(`/spots/api/spots/${spotId}/detail/`);
}

export async function fetchRanking(): Promise<RankingResponse> {
  try {
    return await requestJson<RankingResponse>('/spots/api/ranking/');
  } catch (error) {
    return {
      week_ago: new Date().toISOString(),
      spots: [],
    };
  }
}

export async function fetchRecentSpots(): Promise<SpotsResponse> {
  try {
    return await requestJson<SpotsResponse>('/spots/api/recent-spots/');
  } catch (error) {
    return { spots: [] };
  }
}

export async function fetchSpotsByFilter(filter: SpotFilter): Promise<SpotsResponse> {
  const query = filter === 'all' ? '' : `?filter=${encodeURIComponent(filter)}`;
  try {
    return await requestJson<SpotsResponse>(`/spots/api/spots/${query}`);
  } catch (error) {
    return { spots: [] };
  }
}

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  try {
    return await requestJson<AuthStatusResponse>('/spots/api/auth/me/');
  } catch (error) {
    return { is_authenticated: false };
  }
}

export async function fetchMySpots(): Promise<MySpotsResponse> {
  try {
    return await requestJson<MySpotsResponse>('/spots/api/my-spots/');
  } catch (error) {
    return { spots: [] };
  }
}

export async function fetchProfile(): Promise<ProfileResponse> {
  try {
    return await requestJson<ProfileResponse>('/spots/api/profile/');
  } catch (error) {
    return {
      profile: {
        bio: '',
        avatar: null,
        favorite_spots: [],
      },
      user: {
        id: 0,
        username: '',
        email: '',
      },
    };
  }
}
