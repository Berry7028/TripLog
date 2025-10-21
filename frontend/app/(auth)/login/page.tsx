'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

import { ensureCsrfToken } from '@/lib/csrf';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const token = await ensureCsrfToken();
    if (!token) {
      setError('セキュリティトークンを取得できませんでした。ページを再読み込みしてください。');
      setIsSubmitting(false);
      return;
    }

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token,
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const detail = await response.json();
      setError(detail.error || 'ログインに失敗しました。');
      setIsSubmitting(false);
    } else {
      // 認証状態変更イベントを発火
      window.dispatchEvent(new Event('authStateChanged'));
      router.push('/');
      router.refresh();
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-6">
        <div className="card">
          <div className="card-header text-center">
            <h2>
              <i className="fas fa-sign-in-alt me-2"></i>ログイン
            </h2>
            <p className="text-muted mb-0">お帰りなさい。</p>
          </div>
          <div className="card-body">
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">
                  ユーザー名
                </label>
                <input
                  type="text"
                  id="username"
                  className="form-control"
                  placeholder="ユーザー名を入力"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="password" className="form-label">
                  パスワード
                </label>
                <input
                  type="password"
                  id="password"
                  className="form-control"
                  placeholder="パスワードを入力"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className="d-grid">
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  <i className="fas fa-sign-in-alt me-2"></i>
                  {isSubmitting ? 'ログイン中...' : 'ログイン'}
                </button>
              </div>
            </form>
          </div>
          <div className="card-footer text-center">
            <p className="mb-0">
              アカウントをお持ちでない方は <Link href="/register">新規登録</Link>
            </p>
          </div>
        </div>

        <div className="card mt-4">
          <div className="card-header">
            <h5>
              <i className="fas fa-eye me-2"></i>ゲストとしてご利用の場合
            </h5>
          </div>
          <div className="card-body">
            <p>ログインしなくても以下の機能をご利用いただけます：</p>
            <ul>
              <li>
                <i className="fas fa-search me-2"></i>スポットの検索・閲覧
              </li>
              <li>
                <i className="fas fa-eye me-2"></i>レビューの閲覧
              </li>
              <li>
                <i className="fas fa-map me-2"></i>位置情報の確認
              </li>
            </ul>
            <p className="mb-0">
              <small className="text-muted">スポットの投稿やレビューの投稿にはログインが必要です。</small>
            </p>
            <div className="text-center mt-3">
              <Link href="/" className="btn btn-outline-primary">
                <i className="fas fa-home me-2"></i>ゲストとして続行
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
