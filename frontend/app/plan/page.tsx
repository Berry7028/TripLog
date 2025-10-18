'use client';

export default function PlanPage() {
  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">旅行プランナー</h1>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => {
              const iframe = document.getElementById('planner-iframe') as HTMLIFrameElement | null;
              if (iframe) {
                iframe.src = iframe.src;
              }
            }}
            className="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
          >
            更新
          </button>
          <a
            href="https://maps-planner.vercel.app/"
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
          >
            新しいタブで開く
          </a>
        </div>
      </header>
      <div className="overflow-hidden rounded-3xl border border-slate-200">
        <iframe
          id="planner-iframe"
          src="https://maps-planner.vercel.app/"
          title="プランニングツール"
          className="h-[70vh] w-full min-h-[500px]"
        >
          お使いのブラウザはiframeをサポートしていません。
        </iframe>
      </div>
    </div>
  );
}
