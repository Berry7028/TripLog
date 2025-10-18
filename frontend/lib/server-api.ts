import { buildApiUrl } from './config';

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

export async function fetchHomeSpots(params: QueryParams = {}) {
  const qs = buildQueryString(params);
  return getJson<any>(`/spots/api/home/${qs}`);
}

export async function fetchAuthStatus() {
  return getJson<any>('/spots/api/auth/me/');
}

export async function fetchMySpots() {
  return getJson<any>('/spots/api/my-spots/');
}

export async function fetchSpotDetail(spotId: number) {
  return getJson<any>(`/spots/api/spots/${spotId}/detail/`);
}

export async function fetchProfile() {
  return getJson<any>('/spots/api/profile/');
}

export async function fetchRecentSpots() {
  return getJson<any>('/spots/api/recent-spots/');
}

export async function fetchRanking() {
  return getJson<any>('/spots/api/ranking/');
}

export async function fetchSpotsByFilter(params: QueryParams = {}) {
  const qs = buildQueryString(params);
  return getJson<any>(`/spots/api/spots/${qs}`);
}


