import { WebSocketProvider } from '../components/WebSocketProvider';
import ConnectionStatus from '../components/ConnectionStatus';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../src/app/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Travel Planner - AI-Powered Trip Planning',
  description: 'Plan your perfect trip with AI agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <WebSocketProvider>
          {children}
          <ConnectionStatus />
        </WebSocketProvider>
      </body>
    </html>
  );
}
