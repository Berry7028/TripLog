// Minimal declaration to satisfy TypeScript when @types/leaflet is not installed
declare module 'leaflet' {
  const L: any;
  export default L;
}
