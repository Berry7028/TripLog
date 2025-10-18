export type QueryParams = Record<string, string | string[] | undefined>;

export function buildQueryString(params: QueryParams = {}): string {
  const qs = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => qs.append(key, item));
    } else if (value !== undefined) {
      qs.set(key, value);
    }
  });

  const raw = qs.toString();
  return raw ? `?${raw}` : '';
}
