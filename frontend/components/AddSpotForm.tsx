'use client';

import 'leaflet/dist/leaflet.css';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

import { ensureCsrfToken } from '@/lib/csrf';

type FieldErrorMap = Record<string, string[]>;

const defaultCenter: [number, number] = [35.6762, 139.6503];

const defaultMarkerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = defaultMarkerIcon;

function MapViewSynchronizer({ position }: { position: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.setView(position, Math.max(map.getZoom(), 13));
    }
  }, [map, position]);

  return null;
}

function MapClickHandler({ onSelect }: { onSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(event) {
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });
  return null;
}

async function reverseGeocode(lat: number, lng: number): Promise<string | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&accept-language=ja&lat=${lat}&lon=${lng}`,
    );
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as { display_name?: string };
    return data.display_name ?? null;
  } catch (error) {
    console.warn('Failed to reverse geocode', error);
    return null;
  }
}

async function searchPlace(keyword: string): Promise<{ lat: number; lon: number; displayName: string } | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&accept-language=ja&limit=1&q=${encodeURIComponent(keyword)}`,
    );
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as Array<{ display_name: string; lat: string; lon: string }>;
    if (!data.length) {
      return null;
    }
    const spot = data[0];
    return {
      lat: Number(spot.lat),
      lon: Number(spot.lon),
      displayName: spot.display_name,
    };
  } catch (error) {
    console.warn('Failed to search place', error);
    return null;
  }
}

export default function AddSpotForm() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [address, setAddress] = useState('');
  const [tagsText, setTagsText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageUrlPreview, setImageUrlPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrorMap | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const filePreviewRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (filePreviewRef.current) {
        URL.revokeObjectURL(filePreviewRef.current);
      }
    };
  }, []);

  const mapPosition = useMemo(() => {
    const lat = Number(latitude);
    const lng = Number(longitude);
    if (Number.isFinite(lat) && Number.isFinite(lng)) {
      return [lat, lng] as [number, number];
    }
    return null;
  }, [latitude, longitude]);

  const applyLatLng = async (lat: number, lng: number, updateAddress = true) => {
    const fixedLat = lat.toFixed(6);
    const fixedLng = lng.toFixed(6);
    setLatitude(fixedLat);
    setLongitude(fixedLng);
    if (updateAddress) {
      const resolvedAddress = await reverseGeocode(lat, lng);
      if (resolvedAddress) {
        setAddress(resolvedAddress);
      }
    }
  };

  const handleSearch = async () => {
    const keyword = searchKeyword.trim();
    if (!keyword) {
      return;
    }
    setIsSearching(true);
    setError(null);
    try {
      const result = await searchPlace(keyword);
      if (!result) {
        setError('場所を見つけられませんでした。別のキーワードでお試しください。');
        return;
      }
      setAddress(result.displayName);
      await applyLatLng(result.lat, result.lon, false);
    } finally {
      setIsSearching(false);
    }
  };

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setError('現在地取得がサポートされていません。');
      return;
    }
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude: lat, longitude: lng } = position.coords;
        await applyLatLng(lat, lng);
      },
      () => {
        setError('現在地を取得できませんでした。位置情報の権限を確認してください。');
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    if (filePreviewRef.current) {
      URL.revokeObjectURL(filePreviewRef.current);
      filePreviewRef.current = null;
    }
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      filePreviewRef.current = previewUrl;
      setImagePreview(previewUrl);
    } else {
      setImagePreview(null);
    }
  };

  const handleImageUrlChange = (value: string) => {
    setImageUrl(value);
    const trimmed = value.trim();
    if (trimmed) {
      setImageUrlPreview(trimmed);
    } else {
      setImageUrlPreview(null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setFieldErrors(null);

    const form = event.currentTarget;
    const formData = new FormData(form);

    const token = await ensureCsrfToken();
    if (!token) {
      setError('セキュリティトークンを取得できませんでした。ページを再読み込みしてください。');
      setIsSubmitting(false);
      return;
    }
    formData.set('csrfmiddlewaretoken', token);

    const response = await fetch('/api/spots/add', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': token,
      },
    });

    if (!response.ok) {
      let detail: any = null;
      try {
        detail = await response.json();
      } catch (parseError) {
        detail = null;
      }
      const errors = (detail?.errors ?? null) as FieldErrorMap | null;
      setFieldErrors(errors);
      const firstError = errors ? Object.values(errors)[0]?.[0] : null;
      const errorMessage = detail?.error || firstError;
      setError(errorMessage || 'スポットを投稿できませんでした。入力内容をご確認ください。');
      setIsSubmitting(false);
      return;
    }

    const json = await response.json();
    const spotId = json?.spot?.id;
    if (spotId) {
      router.push(`/spots/${spotId}`);
    } else {
      router.push('/');
    }
    router.refresh();
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h2>
              <i className="fas fa-plus me-2"></i>新しいスポットを投稿
            </h2>
          </div>
          <div className="card-body">
            {error ? (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            ) : null}

            <form method="post" encType="multipart/form-data" onSubmit={handleSubmit} className="needs-validation">
              <div className="mb-3">
                <label htmlFor="add-spot-title" className="form-label">
                  スポット名 *
                </label>
                <input
                  id="add-spot-title"
                  name="title"
                  className={`form-control${fieldErrors?.title ? ' is-invalid' : ''}`}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  required
                />
                {fieldErrors?.title ? <div className="text-danger mt-1">{fieldErrors.title[0]}</div> : null}
              </div>

              <div className="mb-3">
                <label htmlFor="add-spot-description" className="form-label">
                  説明 *
                </label>
                <textarea
                  id="add-spot-description"
                  name="description"
                  className={`form-control${fieldErrors?.description ? ' is-invalid' : ''}`}
                  rows={4}
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  required
                ></textarea>
                {fieldErrors?.description ? <div className="text-danger mt-1">{fieldErrors.description[0]}</div> : null}
              </div>

              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label htmlFor="add-spot-latitude" className="form-label">
                      緯度 *
                    </label>
                    <input
                      id="add-spot-latitude"
                      name="latitude"
                      className={`form-control${fieldErrors?.latitude ? ' is-invalid' : ''}`}
                      type="number"
                      step="any"
                      value={latitude}
                      onChange={(event) => setLatitude(event.target.value)}
                      required
                    />
                    {fieldErrors?.latitude ? <div className="text-danger mt-1">{fieldErrors.latitude[0]}</div> : null}
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label htmlFor="add-spot-longitude" className="form-label">
                      経度 *
                    </label>
                    <input
                      id="add-spot-longitude"
                      name="longitude"
                      className={`form-control${fieldErrors?.longitude ? ' is-invalid' : ''}`}
                      type="number"
                      step="any"
                      value={longitude}
                      onChange={(event) => setLongitude(event.target.value)}
                      required
                    />
                    {fieldErrors?.longitude ? <div className="text-danger mt-1">{fieldErrors.longitude[0]}</div> : null}
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="add-spot-address" className="form-label">
                  住所
                </label>
                <input
                  id="add-spot-address"
                  name="address"
                  className={`form-control${fieldErrors?.address ? ' is-invalid' : ''}`}
                  value={address}
                  onChange={(event) => setAddress(event.target.value)}
                />
                {fieldErrors?.address ? <div className="text-danger mt-1">{fieldErrors.address[0]}</div> : null}
                <div className="form-text text-muted" style={{ fontSize: '0.95em' }}>
                  ※地図をクリックして追加した場合、反映が遅い場合があります
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="add-spot-tags" className="form-label">
                  タグ（任意）
                </label>
                <input
                  id="add-spot-tags"
                  name="tags_text"
                  className="form-control"
                  value={tagsText}
                  onChange={(event) => setTagsText(event.target.value)}
                  placeholder="例: 海, 山, 絶景"
                />
                <div className="form-text">カンマ区切りで入力（例: 海, 山, 絶景）</div>
              </div>

              <div className="mb-3">
                <label className="form-label">地図で位置を選択（任意）</label>
                <div className="input-group mb-2">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="住所や施設名で検索"
                    value={searchKeyword}
                    onChange={(event) => setSearchKeyword(event.target.value)}
                  />
                  <button
                    type="button"
                    className="btn btn-outline-primary"
                    onClick={handleSearch}
                    disabled={isSearching}
                  >
                    <i className="fas fa-search me-1"></i>
                    {isSearching ? '検索中...' : '検索'}
                  </button>
                  <button type="button" className="btn btn-outline-secondary" onClick={handleUseMyLocation}>
                    <i className="fas fa-location-arrow me-1"></i>現在地
                  </button>
                </div>
                <div className="map-frame" style={{ height: '320px', width: '100%' }}>
                  <MapContainer
                    center={mapPosition ?? defaultCenter}
                    zoom={mapPosition ? 13 : 11}
                    scrollWheelZoom
                    style={{ height: '100%', width: '100%' }}
                  >
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    <MapClickHandler
                      onSelect={(lat, lng) => {
                        void applyLatLng(lat, lng);
                      }}
                    />
                    <MapViewSynchronizer position={mapPosition} />
                    {mapPosition ? <Marker position={mapPosition} /> : null}
                  </MapContainer>
                </div>
                <div className="form-text">地図をクリックすると緯度・経度に自動入力されます。</div>
              </div>

              <div className="mb-3">
                <label htmlFor="add-spot-image" className="form-label">
                  画像（アップロード）
                </label>
                <input
                  id="add-spot-image"
                  name="image"
                  type="file"
                  accept="image/*"
                  className={`form-control${fieldErrors?.image ? ' is-invalid' : ''}`}
                  onChange={handleFileChange}
                />
                {fieldErrors?.image ? <div className="text-danger mt-1">{fieldErrors.image[0]}</div> : null}
                <div className="form-text">
                  JPEG/PNG などの画像をアップロード、または下の「画像URL」を入力してください（どちらかでOK）。
                </div>
                {imagePreview ? (
                  <img
                    src={imagePreview}
                    alt="アップロードプレビュー"
                    className="img-thumbnail mt-2"
                    style={{ maxWidth: '200px' }}
                  />
                ) : null}
              </div>

              <div className="mb-3">
                <label htmlFor="add-spot-image-url" className="form-label">
                  画像URL（任意）
                </label>
                <input
                  id="add-spot-image-url"
                  name="image_url"
                  type="url"
                  className={`form-control${fieldErrors?.image_url ? ' is-invalid' : ''}`}
                  value={imageUrl}
                  onChange={(event) => handleImageUrlChange(event.target.value)}
                />
                {fieldErrors?.image_url ? <div className="text-danger mt-1">{fieldErrors.image_url[0]}</div> : null}
                <div className="form-text">例: https://example.com/path/to/photo.jpg</div>
                {imageUrlPreview ? (
                  <img
                    src={imageUrlPreview}
                    alt="URL プレビュー"
                    className="img-thumbnail mt-2"
                    style={{ maxWidth: '200px' }}
                  />
                ) : null}
              </div>

              <div className="d-grid gap-2 d-md-flex justify-content-md-end">
                <Link href="/" className="btn btn-secondary me-md-2">
                  <i className="fas fa-times me-2"></i>キャンセル
                </Link>
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  <i className="fas fa-paper-plane me-2"></i>
                  {isSubmitting ? '投稿中...' : '投稿する'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
