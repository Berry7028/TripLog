import type { ReviewPayload } from '@/types/api';

interface ReviewListProps {
  reviews: ReviewPayload[];
  avgRating: number | null;
}

export default function ReviewList({ reviews, avgRating }: ReviewListProps) {
  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">レビュー</h3>
        <span className="text-sm text-slate-500">平均評価: {avgRating ? avgRating.toFixed(1) : '未評価'}</span>
      </header>
      {reviews.length === 0 ? (
        <p className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-500">まだレビューはありません。</p>
      ) : (
        <ul className="space-y-3">
          {reviews.map((review) => (
            <li key={review.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between text-sm text-slate-600">
                <span className="font-semibold text-slate-800">{review.user.username}</span>
                <span>{review.rating} ★</span>
              </div>
              <p className="mt-2 text-sm text-slate-700">{review.comment}</p>
              {review.created_at ? (
                <p className="mt-1 text-xs text-slate-400">{new Date(review.created_at).toLocaleString('ja-JP')}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
