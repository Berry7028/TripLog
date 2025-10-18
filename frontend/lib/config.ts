const rawBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.API_BASE_URL ||
  'http://localhost:8000';

const normalizedBaseUrl = rawBaseUrl.replace(/\/$/, '');

export const API_BASE_URL = normalizedBaseUrl;
