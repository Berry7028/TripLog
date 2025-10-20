import { NextRequest } from 'next/server';

import { forwardJson } from '../../../_utils/forward';

interface Params {
  params: { id: string };
}

export async function POST(request: NextRequest, { params }: Params) {
  return forwardJson(request, `/api/spots/${params.id}/favorite-toggle/`);
}
