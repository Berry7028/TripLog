'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

import { ensureCsrfToken } from '@/lib/csrf';

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (password1 !== password2) {
      setError('パスワードが一致しません。');
      return;
    }
    setIsSubmitting(true);
    setError(null);

    const token = await ensureCsrfToken();
    if (!token) {
      setError('セキュリティトークンを取得できませんでした。ページを再読み込みしてください。');
      setIsSubmitting(false);
      return;
    }

    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token,
      },
      body: JSON.stringify({ username, password1, password2 }),
    });

    if (!response.ok) {
      const detail = await response.json();
      const errorMessage =
        detail.error || (detail.errors && Object.values(detail.errors as Record<string, string[]>)[0]?.[0]);
      setError(errorMessage || '登録に失敗しました。');
    } else {
      router.push('/');
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-6">
        <div className="card">
          <div className="card-header text-center">
            <h2>
              <i className="fas fa-user-plus me-2"></i>新規登録
            </h2>
            <p className="text-muted mb-0">旅ログマップへようこそ！</p>
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
                <div className="form-text">150文字以下で入力してください。英数字と @/./+/-/_ のみ使用可能です。</div>
              </div>

              <div className="mb-3">
                <label htmlFor="password1" className="form-label">
                  パスワード
                </label>
                <input
                  type="password"
                  id="password1"
                  className="form-control"
                  placeholder="パスワードを入力"
                  autoComplete="new-password"
                  value={password1}
                  onChange={(e) => setPassword1(e.target.value)}
                  required
                />
                <div className="form-text">
                  <ul className="mb-0">
                    <li>他の個人情報と類似していないこと</li>
                    <li>最低8文字以上であること</li>
                    <li>一般的すぎるパスワードでないこと</li>
                    <li>数字のみでないこと</li>
                  </ul>
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="password2" className="form-label">
                  パスワード（確認）
                </label>
                <input
                  type="password"
                  id="password2"
                  className="form-control"
                  placeholder="もう一度入力"
                  autoComplete="new-password"
                  value={password2}
                  onChange={(e) => setPassword2(e.target.value)}
                  required
                />
                <div className="form-text">確認のため、上記と同じパスワードを入力してください。</div>
              </div>

              <div className="d-grid">
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  <i className="fas fa-user-plus me-2"></i>
                  {isSubmitting ? '登録中...' : 'アカウントを作成'}
                </button>
              </div>
            </form>
          </div>
          <div className="card-footer text-center">
            <p className="mb-0">
              既にアカウントをお持ちですか？ <Link href="/login">ログイン</Link>
            </p>
          </div>
        </div>

        <div className="card mt-4">
          <div className="card-header">
            <h5>
              <i className="fas fa-info-circle me-2"></i>旅ログマップでできること
            </h5>
          </div>
          <div className="card-body">
            <div className="row text-center">
              <div className="col-md-4 mb-3">
                <i className="fas fa-map-marked-alt fa-2x text-primary mb-2"></i>
                <h6>スポット投稿</h6>
                <p className="text-muted small">お気に入りの場所を写真と一緒に投稿</p>
              </div>
              <div className="col-md-4 mb-3">
                <i className="fas fa-star fa-2x text-warning mb-2"></i>
                <h6>レビュー機能</h6>
                <p className="text-muted small">他の人の投稿にレビューを投稿</p>
              </div>
              <div className="col-md-4 mb-3">
                <i className="fas fa-search fa-2x text-success mb-2"></i>
                <h6>スポット検索</h6>
                <p className="text-muted small">行きたい場所を簡単に検索</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
