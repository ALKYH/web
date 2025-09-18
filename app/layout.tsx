import type { Metadata } from 'next';
import localFont from 'next/font/local';
import './globals.css';
import Navbar from '@/components/base/navbar';
import Footer from '@/components/base/footer';
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import { AuthInitializer } from '@/components/auth/auth-initializer';
import ChatWidget from '@/components/ui/chat-widget';
import { FirstVisitModal } from '@/components/first-visit/first-visit-modal';

const geistSans = localFont({
  src: '../fonts/GeistVariableVF.woff2',
  variable: '--font-geist-sans',
  display: 'swap'
});

const geistMono = localFont({
  src: '../fonts/GeistMonoVariableVF.woff2',
  variable: '--font-geist-mono',
  display: 'swap'
});

export const metadata: Metadata = {
  title: 'OfferIn',
  description: 'OfferIn 留学 - 留学申请一站式平台',
  icons: {
    icon: '/icon.png'
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthInitializer>
          <Navbar />
          <NuqsAdapter>{children}</NuqsAdapter>
          <Footer />
          <ChatWidget />
          <FirstVisitModal />
        </AuthInitializer>
      </body>
    </html>
  );
}
