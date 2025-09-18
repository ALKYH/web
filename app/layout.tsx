import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/base/navbar';
import Footer from '@/components/base/footer';
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import { AuthInitializer } from '@/components/auth/auth-initializer';
import ChatWidget from '@/components/ui/chat-widget';
import { FirstVisitModal } from '@/components/first-visit/first-visit-modal';
import { ConfigProvider } from 'antd';
import antdTheme from '@/lib/antd-theme';

// 暂时抑制React 19兼容性警告
if (typeof window !== 'undefined') {
  const originalWarn = console.warn;
  console.warn = (...args) => {
    if (args[0]?.includes?.('antd: compatible')) {
      return;
    }
    originalWarn(...args);
  };
}

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin']
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin']
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
        <ConfigProvider theme={antdTheme}>
          <AuthInitializer>
            <Navbar />
            <NuqsAdapter>{children}</NuqsAdapter>
            <Footer />
            <ChatWidget />
            <FirstVisitModal />
          </AuthInitializer>
        </ConfigProvider>
      </body>
    </html>
  );
}
