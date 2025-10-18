'use client';

import { useEffect, useMemo, useState } from 'react';

import SpotMap from './SpotMap';
import SpotMapSidebar from './SpotMapSidebar';
import { fetchSpotsByFilter } from '@/lib/server-api';
import type { SpotFilter, SpotSummary } from '@/types/api';

interface SpotMapLayoutProps {
  initialSpots: SpotSummary[];
  recentSpots: SpotSummary[];
  isAuthenticated: boolean;
}

export default function SpotMapLayout({ initialSpots, recentSpots, isAuthenticated }: SpotMapLayoutProps) {
  const [filter, setFilter] = useState<SpotFilter>('all');
  const [spots, setSpots] = useState<SpotSummary[]>(initialSpots);
  const [selectedSpot, setSelectedSpot] = useState<SpotSummary | null>(initialSpots[0] ?? null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSpots(initialSpots);
    setSelectedSpot((prev) => {
      if (!initialSpots.length) {
        return null;
      }
      if (prev) {
        const matched = initialSpots.find((spot) => spot.id === prev.id);
        if (matched) {
          return matched;
        }
      }
      return initialSpots[0];
    });
  }, [initialSpots]);

  useEffect(() => {
    let cancelled = false;

    if (filter === 'all') {
      setSpots(initialSpots);
      setError(null);
      setIsLoading(false);
      return undefined;
    }

    setIsLoading(true);
    setError(null);

    fetchSpotsByFilter({ filter })
      .then((response) => {
        if (!cancelled) {
          setSpots(response.spots);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setSpots([]);
          setError('フィルタ適用中にエラーが発生しました。');
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [filter, initialSpots]);

  useEffect(() => {
    setSelectedSpot((prev) => {
      if (!spots.length) {
        return null;
      }
      if (prev) {
        const matched = spots.find((spot) => spot.id === prev.id);
        if (matched) {
          return matched;
        }
      }
      return spots[0];
    });
  }, [spots]);

  const handleFilterChange = (nextFilter: SpotFilter) => {
    setFilter(nextFilter);
  };

  const handleSelectRecentSpot = (spot: SpotSummary) => {
    setFilter('all');
    setSelectedSpot(spot);
  };

  const sidebarSelectedSpot = useMemo(() => selectedSpot, [selectedSpot]);

  return (
    <div className="row mt-2 mb-3">
      <div className="col-md-8">
        <div className="map-surface" style={{ height: '80vh', minHeight: '600px' }}>
          <SpotMap
            spots={spots}
            filter={filter}
            onSelect={setSelectedSpot}
            selectedSpotId={selectedSpot?.id ?? null}
          />
        </div>
      </div>
      <div className="col-md-4">
        <SpotMapSidebar
          selectedSpot={sidebarSelectedSpot}
          filter={filter}
          onFilterChange={handleFilterChange}
          isAuthenticated={isAuthenticated}
          recentSpots={recentSpots}
          onSelectRecentSpot={handleSelectRecentSpot}
          isLoading={isLoading}
          error={error}
        />
      </div>
    </div>
  );
}
