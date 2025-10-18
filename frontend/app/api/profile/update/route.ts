import { NextRequest } from 'next/server';

import { forwardFormData } from '../../_utils/forward';

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  return forwardFormData(request, '/spots/api/profile/', formData);
}
