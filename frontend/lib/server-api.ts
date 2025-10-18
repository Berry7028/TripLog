import type {
  AuthStatusResponse,
  HomeResponse,
  MySpotsResponse,
  ProfileResponse,
  RankingResponse,
  SpotDetailResponse,
  SpotsResponse,
} from '@/types/api';
import { API_BASE_URL } from './config';

class HttpError extends Error {
  status: number;
  body?: string;

  constructor(status: number, body?: string) {
    super(`Request failed with status ${status}`);
    this.status = status;
    this.body = body;
  }
}

async function getServerCookieHeader(): Promise<string | undefined> {
  if (typeof window !== 'undefined') {
    return undefined;
  }
  try {
    const { cookies } = await import('next/headers');
    const store = cookies();
    const entries = store.getAll();
    if (entries.length === 0) {
      return undefined;
    }
    return entries.map((item) => `${item.name}=${item.value}`).join('; ');
  } catch (error) {
    return undefined;
  }
}

async function fetchJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { headers: initHeaders, ...init } = options;
  const headers = new Headers(initHeaders);
  headers.set('Accept', 'application/json');

  const isServer = typeof window === 'undefined';
  if (!isServer && !init.credentials) {
    init.credentials = 'include';
  }
  if (isServer) {
    init.cache = 'no-store';
    const cookieHeader = await getServerCookieHeader();
    if (cookieHeader) {
      headers.set('Cookie', cookieHeader);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const bodyText = await response.text().catch(() => undefined);
    throw new HttpError(response.status, bodyText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function createQueryString(params: Record<string, string | string[] | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined) {
          search.append(key, item);
        }
      });
    } else if (value !== undefined) {
      search.set(key, value);
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function fetchHomeSpots(
  searchParams: Record<string, string | string[] | undefined> = {},
): Promise<HomeResponse> {
  const query = createQueryString(searchParams);
  return fetchJson<HomeResponse>(`/spots/api/home/${query}`);
}

export async function fetchRanking(): Promise<RankingResponse> {
  return fetchJson<RankingResponse>('/spots/api/ranking/');
}

export async function fetchRecentSpots(): Promise<SpotsResponse> {
  return fetchJson<SpotsResponse>('/spots/api/recent-spots/');
}

export async function fetchSpotDetail(spotId: number): Promise<SpotDetailResponse> {
  return fetchJson<SpotDetailResponse>(`/spots/api/spots/${spotId}/detail/`);
}

export async function fetchMySpots(): Promise<MySpotsResponse> {
  try {
    return await fetchJson<MySpotsResponse>('/spots/api/my-spots/');
  } catch (error) {
    if (error instanceof HttpError && (error.status === 401 || error.status === 403)) {
      return { spots: [] };
    }
    throw error;
  }
}

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  try {
    return await fetchJson<AuthStatusResponse>('/spots/api/auth/me/');
  } catch (error) {
    if (error instanceof HttpError && (error.status === 401 || error.status === 403)) {
      return { is_authenticated: false };
    }
    throw error;
  }
}

export async function fetchProfile(): Promise<ProfileResponse> {
  const [profile, auth] = await Promise.all([
    fetchJson<ProfileResponse>('/spots/api/profile/'),
    fetchAuthStatus(),
  ]);

  const favoriteCount = auth.stats?.favorite_count ?? profile.profile.favorite_spots.length;
  return {
    ...profile,
    user: {
      ...profile.user,
      date_joined: auth.user?.date_joined ?? profile.user.date_joined,
    },
    stats: {
      spot_count: auth.stats?.spot_count ?? 0,
      review_count: auth.stats?.review_count ?? 0,
      favorite_count: favoriteCount,
    },
    recent_activity: auth.recent_activity ?? { spots: [], reviews: [] },
  };
}
