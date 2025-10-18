import { NextRequest } from 'next/server';

import { forwardJson } from '../../_utils/forward';

export async function POST(request: NextRequest) {
  return forwardJson(request, '/spots/api/auth/login/');
}
