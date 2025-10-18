// Prefer explicit Next.js public var for Django base, then other API vars, then fallback
const rawBaseUrl =
  process.env.NEXT_PUBLIC_DJANGO_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.API_BASE_URL ||
  'http://localhost:8000';

const normalizedBaseUrl = rawBaseUrl.replace(/\/$/, '');

export const API_BASE_URL = normalizedBaseUrl;

export function buildApiUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
