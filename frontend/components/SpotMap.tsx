'use client';

import 'leaflet/dist/leaflet.css';

import { useMemo, useEffect } from 'react';
import Link from 'next/link';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';

import type { SpotFilter, SpotSummary } from '@/types/api';

interface SpotMapProps {
  spots: SpotSummary[];
  filter: SpotFilter;
  onSelect?: (spot: SpotSummary) => void;
  selectedSpotId?: number | null;
}

const defaultPosition: [number, number] = [35.681236, 139.767125];

const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = defaultIcon;

function MapAutoCenter({ center }: { center: [number, number] }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);

  return null;
}

export default function SpotMap({ spots, filter, onSelect, selectedSpotId }: SpotMapProps) {
  const activeCenter = useMemo(() => {
    if (selectedSpotId != null) {
      const selected = spots.find((spot) => spot.id === selectedSpotId);
      if (selected) {
        return [selected.latitude, selected.longitude] as [number, number];
      }
    }
    if (spots.length > 0) {
      return [spots[0].latitude, spots[0].longitude] as [number, number];
    }
    return defaultPosition;
  }, [selectedSpotId, spots]);

  return (
    <div className="relative h-[600px] w-full overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <MapContainer
        {...({ center: activeCenter, zoom: 6, scrollWheelZoom: true, className: 'h-full w-full' } as any)}
      >
        <MapAutoCenter center={activeCenter} />
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {spots.map((spot) => (
          <Marker
            key={spot.id}
            position={[spot.latitude, spot.longitude] as [number, number]}
            eventHandlers={{
              click: () => {
                onSelect?.(spot);
              },
            }}
          >
            <Popup>
              <div className="space-y-1 text-sm">
                <strong>{spot.title}</strong>
                <p className="text-xs text-slate-500">{spot.address}</p>
                <Link href={`/spots/${spot.id}`} className="text-primary">
                  詳細を見る
                </Link>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      {spots.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 text-center text-sm text-slate-500">
          {filter === 'mine'
            ? 'まだ自分の投稿がありません。'
            : filter === 'others'
              ? '他のユーザーの投稿が見つかりませんでした。'
              : '表示できるスポットがありません。'}
        </div>
      )}
    </div>
  );
}
