import { NextRequest, NextResponse } from 'next/server';

import { API_BASE_URL } from '@/lib/config';

import { copySetCookie } from '../../_utils/forward';

export async function GET(request: NextRequest) {
  const cookieHeader = request.headers.get('cookie') || undefined;
  const headers = new Headers();
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }

  const response = await fetch(`${API_BASE_URL}/api/profile/`, {
    method: 'GET',
    headers,
    redirect: 'manual',
  });

  const nextResponse = NextResponse.json(
    { success: response.ok },
    { status: response.ok ? 200 : response.status },
  );
  copySetCookie(response, nextResponse);
  return nextResponse;
}
