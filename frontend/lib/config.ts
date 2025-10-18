const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_DJANGO_BASE_URL?.replace(/\/?$/, '/') ?? DEFAULT_API_BASE_URL + '/';

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_BASE_URL}${normalizedPath}`;
}
