const candidateEnvValues = [
  process.env.NEXT_PUBLIC_DJANGO_BASE_URL,
  process.env.NEXT_PUBLIC_API_BASE_URL,
  process.env.NEXT_PUBLIC_BACKEND_URL,
];

const rawBaseUrl = candidateEnvValues.find(
  (value): value is string => typeof value === 'string' && value.trim().length > 0,
);

// Prefer explicit Next.js public var for Django base, then other API vars, then fallback
const normalizedBaseUrl = (rawBaseUrl || 'http://localhost:8000').replace(/\/+$/, '');

export const API_BASE_URL = normalizedBaseUrl;

export function resolveApiBaseUrl(): string {
  return API_BASE_URL;
}

export function buildApiUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
