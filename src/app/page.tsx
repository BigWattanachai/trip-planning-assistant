'use client';

import { useState } from 'react';
import Canvas from '@/components/Canvas/Canvas';
import ChatInterface from '@/components/Chat/ChatInterface';
import Header from '@/components/Layout/Header';
import { TripPlanningProvider } from '@/context/TripPlanningContext';

export default function Home() {
  const [isPlanning, setIsPlanning] = useState(false);

  return (
    <TripPlanningProvider>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <Header />
        
        <main className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
            {/* Canvas Section - Takes 8 columns on large screens */}
            <div className="lg:col-span-8 bg-white rounded-xl shadow-lg overflow-hidden">
              <Canvas isPlanning={isPlanning} />
            </div>
            
            {/* Chat Interface - Takes 4 columns on large screens */}
            <div className="lg:col-span-4 bg-white rounded-xl shadow-lg overflow-hidden">
              <ChatInterface onPlanningStart={() => setIsPlanning(true)} onPlanningComplete={() => setIsPlanning(false)} />
            </div>
          </div>
        </main>
      </div>
    </TripPlanningProvider>
  );
}
