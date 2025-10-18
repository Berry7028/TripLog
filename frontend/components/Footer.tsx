export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-2 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:px-6 lg:px-8">
        <span>© {new Date().getFullYear()} 旅ログマップ</span>
        <span>Next.js + Tailwind CSS フロントエンド</span>
      </div>
    </footer>
  );
}
