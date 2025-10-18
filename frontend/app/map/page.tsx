import SpotMapLayout from '@/components/SpotMapLayout';
import { fetchAuthStatus, fetchRecentSpots } from '@/lib/server-api';

export default async function MapPage() {
  const [auth, recent] = await Promise.all([fetchAuthStatus(), fetchRecentSpots()]);
  const spots = recent.spots;

  return <SpotMapLayout initialSpots={spots} recentSpots={spots.slice(0, 10)} isAuthenticated={auth.is_authenticated} />;
}
