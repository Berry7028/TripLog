'use client';

import 'leaflet/dist/leaflet.css';

import Link from 'next/link';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import L from 'leaflet';

import type { SpotSummary } from '@/types/api';

interface SpotMapProps {
  spots: SpotSummary[];
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

export default function SpotMap({ spots }: SpotMapProps) {
  return (
    <MapContainer
      center={spots.length ? ([spots[0].latitude, spots[0].longitude] as [number, number]) : defaultPosition}
      zoom={6}
      scrollWheelZoom
      className="h-[600px] w-full rounded-2xl"
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {spots.map((spot) => (
        <Marker key={spot.id} position={[spot.latitude, spot.longitude] as [number, number]}>
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
  );
}
