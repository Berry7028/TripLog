const baseUrl = process.env.NEXT_PUBLIC_DJANGO_BASE_URL || 'http://localhost:8000';

export const API_BASE_URL = baseUrl.replace(/\/$/, '');
