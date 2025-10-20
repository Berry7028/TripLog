import { NextRequest, NextResponse } from 'next/server';

import { buildApiUrl } from '@/lib/config';

async function parseResponseBody(response: Response): Promise<any> {
  const contentType = response.headers.get('content-type') || '';
  const text = await response.text();
  if (!text) {
    return null;
  }
  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(text);
    } catch (error) {
      return { raw: text };
    }
  }
  return { raw: text };
}

export function copySetCookie(from: Response, to: NextResponse) {
  const responseHeaders = from.headers as unknown as { getSetCookie?: () => string[] };
  const cookies = responseHeaders.getSetCookie?.() || [];
  if (cookies.length === 0) {
    const single = from.headers.get('set-cookie');
    if (single) {
      to.headers.append('set-cookie', single);
    }
    return;
  }
  cookies.forEach((cookie) => {
    to.headers.append('set-cookie', cookie);
  });
}

export async function forwardJson(request: NextRequest, path: string, init: RequestInit = {}): Promise<NextResponse> {
  const cookieHeader = request.headers.get('cookie') || undefined;
  const headers = new Headers(init.headers);
  headers.set('Content-Type', 'application/json');
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }
  const csrfHeader = request.headers.get('x-csrftoken');
  if (csrfHeader) {
    headers.set('X-CSRFToken', csrfHeader);
  }
  const referer = request.headers.get('referer');
  if (referer) {
    headers.set('Referer', referer);
  }

  const rawBody = await request.text();

  // Only attach a body for methods that allow it (not GET or HEAD).
  const method = (init.method || request.method || 'GET').toUpperCase();
  const bodyToSend = init.body ?? (rawBody.length > 0 && method !== 'GET' && method !== 'HEAD' ? rawBody : undefined);

  const { body: _ignoredBody, method: _ignoredMethod, headers: _ignoredHeaders, ...rest } = init;

  const targetUrl = buildApiUrl(path);
  const response = await fetch(targetUrl, {
    ...rest,
    method,
    headers,
    ...(bodyToSend !== undefined ? { body: bodyToSend } : {}),
    redirect: 'manual',
  });

  const body = await parseResponseBody(response);
  const nextResponse = NextResponse.json(body, { status: response.status });
  copySetCookie(response, nextResponse);
  return nextResponse;
}

export async function forwardFormData(request: NextRequest, path: string, formData: FormData): Promise<NextResponse> {
  const cookieHeader = request.headers.get('cookie') || undefined;
  const headers = new Headers();
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }
  const csrfHeader = request.headers.get('x-csrftoken');
  if (csrfHeader) {
    headers.set('X-CSRFToken', csrfHeader);
  }
  const referer = request.headers.get('referer');
  if (referer) {
    headers.set('Referer', referer);
  }

  const targetUrl = buildApiUrl(path);
  const response = await fetch(targetUrl, {
    method: 'POST',
    headers,
    body: formData,
    redirect: 'manual',
  });

  const body = await parseResponseBody(response);
  const nextResponse = NextResponse.json(body, { status: response.status });
  copySetCookie(response, nextResponse);
  return nextResponse;
}
