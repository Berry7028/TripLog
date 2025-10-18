import type { Metadata } from 'next';
import './globals.css';

import Footer from '@/components/Footer';
import Header from '@/components/Header';

export const metadata: Metadata = {
  title: '旅ログまっぷ',
  description: '旅行スポット共有サービス TripLog',
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja" className="bg-[#FFF5F2]">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Mochiy+Pop+P+One&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
      </head>
      <body className="flex min-h-screen flex-col bg-[#FFF5F2]" style={{ fontFamily: "'Mochiy Pop P One', sans-serif" }}>
        <Header />
        <main className="flex-1">
          <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>
        </main>
        <Footer />
      </body>
    </html>
  );
}
