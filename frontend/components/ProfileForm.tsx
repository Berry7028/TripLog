'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useEffect, useState } from 'react';

import type { ProfileResponse } from '@/types/api';

interface ProfileFormProps {
  profile: ProfileResponse['profile'];
  user: ProfileResponse['user'];
}

export default function ProfileForm({ profile, user }: ProfileFormProps) {
  const router = useRouter();
  const [bio, setBio] = useState(profile.bio);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(profile.avatar);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setAvatarFile(file);
    if (avatarPreview && avatarPreview.startsWith('blob:')) {
      URL.revokeObjectURL(avatarPreview);
    }
    if (file) {
      setAvatarPreview(URL.createObjectURL(file));
    } else {
      setAvatarPreview(profile.avatar ?? null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.set('bio', bio);
    if (avatarFile) {
      formData.set('avatar', avatarFile);
    }

    try {
      const response = await fetch('/api/profile/update', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        const errors = detail.errors as Record<string, string[]> | undefined;
        const firstError = errors ? Object.values(errors)[0]?.[0] : undefined;
        const message = detail.error || firstError || 'プロフィールを更新できませんでした。';
        setError(message);
      } else {
        router.refresh();
      }
    } catch (submitError) {
      setError('プロフィールを更新できませんでした。');
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    return () => {
      if (avatarPreview && avatarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(avatarPreview);
      }
    };
  }, [avatarPreview]);

  return (
    <form onSubmit={handleSubmit} encType="multipart/form-data">
      {error ? (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      ) : null}

      <div className="row">
        <div className="col-md-4 text-center">
          {avatarPreview ? (
            <img
              src={avatarPreview}
              alt="アバター"
              className="img-thumbnail mb-3"
              style={{ width: '150px', height: '150px', objectFit: 'cover' }}
            />
          ) : (
            <div
              className="bg-light d-flex align-items-center justify-content-center mb-3"
              style={{ width: '150px', height: '150px', margin: '0 auto' }}
            >
              <i className="fas fa-user fa-4x text-muted"></i>
            </div>
          )}

          <div className="mb-3">
            <label htmlFor="profile-avatar" className="form-label">
              アバター画像
            </label>
            <input
              id="profile-avatar"
              type="file"
              accept="image/*"
              className="form-control"
              onChange={handleFileChange}
            />
          </div>
        </div>

        <div className="col-md-8">
          <div className="mb-3">
            <label className="form-label">ユーザー名</label>
            <input type="text" className="form-control" value={user.username} readOnly />
            <div className="form-text">ユーザー名は変更できません。</div>
          </div>

          <div className="mb-3">
            <label className="form-label">メールアドレス</label>
            <input type="email" className="form-control" value={user.email || '未設定'} readOnly />
            <div className="form-text">メールアドレスの変更は管理者にお問い合わせください。</div>
          </div>

          <div className="mb-3">
            <label htmlFor="profile-bio" className="form-label">
              自己紹介
            </label>
            <textarea
              id="profile-bio"
              className="form-control"
              rows={4}
              value={bio}
              onChange={(event) => setBio(event.target.value)}
            ></textarea>
            <div className="form-text">あなたの旅行の趣味や好きな場所について教えてください。</div>
          </div>
        </div>
      </div>

      <div className="d-grid gap-2 d-md-flex justify-content-md-end">
        <Link href="/my-spots" className="btn btn-secondary me-md-2">
          <i className="fas fa-arrow-left me-2"></i>マイページに戻る
        </Link>
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          <i className="fas fa-save me-2"></i>
          {isSubmitting ? '保存中…' : '保存する'}
        </button>
      </div>
    </form>
  );
}
