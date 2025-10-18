import type { Metadata } from 'next';
import { Noto_Sans_JP } from 'next/font/google';
import './globals.css';

import Footer from '@/components/Footer';
import Header from '@/components/Header';

const notoSans = Noto_Sans_JP({ subsets: ['latin'], display: 'swap' });

export const metadata: Metadata = {
  title: '旅ログマップ - Next.js フロントエンド',
  description: '旅行スポット共有サービス TripLog の Next.js + Tailwind CSS フロントエンド',
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja" className="bg-slate-50">
      <body className={`${notoSans.className} flex min-h-screen flex-col bg-slate-50`}>
        <Header />
        <main className="flex-1">
          <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>
        </main>
        <Footer />
      </body>
    </html>
  );
}
