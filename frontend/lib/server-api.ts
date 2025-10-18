import { API_BASE_URL } from './config';
import type {
  AuthStatusResponse,
  HomeResponse,
  MySpotsResponse,
  ProfileResponse,
  RankingResponse,
  SpotDetailResponse,
  SpotsResponse,
} from '@/types/api';

export interface ApiErrorDetail {
  error?: string;
  errors?: Record<string, string[]>;
  [key: string]: unknown;
}

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail;

  constructor(status: number, detail: ApiErrorDetail, message?: string) {
    super(message ?? detail.error ?? 'APIリクエストに失敗しました。');
    this.status = status;
    this.detail = detail;
  }
}

type QueryValue = string | number | boolean | null | undefined;
type QueryRecord = Record<string, QueryValue | QueryValue[]>;

interface ApiFetchOptions extends RequestInit {
  query?: QueryRecord;
}

type MinimalCookie = { name: string; value: string };
type CookieStore = { getAll(): MinimalCookie[] };

let defaultCookiesGetter: (() => CookieStore) | null = null;

function getServerCookieHeader(): string | undefined {
  if (typeof window !== 'undefined') {
    return undefined;
  }

  if (!defaultCookiesGetter) {
    try {
      const mod = require('next/headers') as { cookies: () => CookieStore };
      defaultCookiesGetter = mod.cookies;
    } catch (error) {
      return undefined;
    }
  }

  try {
    const store = defaultCookiesGetter?.();
    if (!store) {
      return undefined;
    }
    const serialized = store
      .getAll()
      .map(({ name, value }) => `${name}=${value}`)
      .join('; ');
    return serialized || undefined;
  } catch (error) {
    return undefined;
  }
}

function buildUrl(path: string, query?: QueryRecord): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(normalizedPath, API_BASE_URL);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === null || value === undefined) {
        return;
      }
      if (Array.isArray(value)) {
        value.forEach((item) => {
          if (item === null || item === undefined) {
            return;
          }
          url.searchParams.append(key, String(item));
        });
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }

  return url.toString();
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    return {} as T;
  }
  try {
    return JSON.parse(text) as T;
  } catch (error) {
    throw new Error('APIレスポンスの解析に失敗しました。');
  }
}

async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { query, headers: initHeaders, cache, next, credentials, ...rest } = options;
  const url = buildUrl(path, query);

  const headers = new Headers(initHeaders);
  headers.set('Accept', 'application/json');

  if (typeof rest.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const cookieHeader = getServerCookieHeader();
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }

  const fetchInit: RequestInit & { next?: any } = {
    ...rest,
    headers,
    credentials: credentials ?? 'include',
  };

  if (cache !== undefined) {
    fetchInit.cache = cache;
  }

  fetchInit.next = next ?? { revalidate: 0 };

  if (
    fetchInit.cache === undefined &&
    fetchInit.next &&
    typeof fetchInit.next === 'object' &&
    'revalidate' in fetchInit.next &&
    fetchInit.next.revalidate === 0
  ) {
    fetchInit.cache = 'no-store';
  }

  const response = await fetch(url, fetchInit);

  if (!response.ok) {
    let detail: ApiErrorDetail = {};
    try {
      detail = await parseJson<ApiErrorDetail>(response);
    } catch (error) {
      detail = { error: response.statusText || 'リクエストに失敗しました。' };
    }
    if (!detail.error && !detail.errors) {
      detail.error = 'リクエストに失敗しました。';
    }
    throw new ApiError(response.status, detail);
  }

  return parseJson<T>(response);
}

function normalizeSearchParams(
  params: Record<string, string | string[] | undefined>,
): QueryRecord {
  const query: QueryRecord = {};
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined) {
      return;
    }
    if (Array.isArray(value)) {
      query[key] = value.filter((item) => item !== undefined && item !== null);
    } else {
      query[key] = value;
    }
  });
  return query;
}

export async function fetchHomeSpots(
  searchParams: Record<string, string | string[] | undefined>,
): Promise<HomeResponse> {
  return apiFetch<HomeResponse>('/spots/api/home/', {
    query: normalizeSearchParams(searchParams),
    next: { revalidate: 0 },
    cache: 'no-store',
  });
}

export async function fetchRanking(): Promise<RankingResponse> {
  return apiFetch<RankingResponse>('/spots/api/ranking/', {
    next: { revalidate: 600 },
    cache: 'force-cache',
  });
}

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  return apiFetch<AuthStatusResponse>('/spots/api/auth/me/', {
    next: { revalidate: 0 },
    cache: 'no-store',
  });
}

export async function fetchMySpots(): Promise<MySpotsResponse> {
  return apiFetch<MySpotsResponse>('/spots/api/my-spots/', {
    next: { revalidate: 0 },
    cache: 'no-store',
  });
}

export async function fetchProfile(): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>('/spots/api/profile/', {
    next: { revalidate: 0 },
    cache: 'no-store',
  });
}

export async function fetchRecentSpots(): Promise<SpotsResponse> {
  return apiFetch<SpotsResponse>('/spots/api/recent-spots/', {
    next: { revalidate: 300 },
  });
}

export async function fetchSpotDetail(spotId: number): Promise<SpotDetailResponse> {
  return apiFetch<SpotDetailResponse>(`/spots/api/spots/${spotId}/detail/`, {
    next: { revalidate: 0 },
    cache: 'no-store',
  });
}
