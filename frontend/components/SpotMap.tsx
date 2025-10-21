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

const defaultPosition: [number, number] = [35.6762, 139.6503];

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
    <div className="map-frame" style={{ height: '100%', minHeight: '600px', width: '100%' }}>
      <MapContainer
        center={activeCenter}
        zoom={10}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
        className="h-100 w-100"
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
              <div className="text-sm">
                <strong>{spot.title}</strong>
                <p className="text-muted small mb-1">{spot.address}</p>
                <Link href={`/spots/${spot.id}`} className="btn btn-primary btn-sm">
                  詳細を見る
                </Link>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      {spots.length === 0 && (
        <div className="d-flex align-items-center justify-content-center text-muted small" style={{ height: '100%' }}>
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
