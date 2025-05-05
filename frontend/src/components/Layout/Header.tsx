import React from 'react';
import { Plane } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-primary-500 p-2 rounded-lg">
            <Plane className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Travel Planner</h1>
            <p className="text-sm text-gray-600">AI-Powered Trip Planning Assistant</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
