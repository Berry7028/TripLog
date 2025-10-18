export const API_BASE_URL =
  process.env.NEXT_PUBLIC_DJANGO_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';

export function buildApiUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
