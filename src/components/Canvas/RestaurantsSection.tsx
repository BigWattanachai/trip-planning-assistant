import React from 'react';
import { Utensils, Star, DollarSign } from 'lucide-react';

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  priceRange: string;
  rating: number;
  reviewHighlight: string;
  imageUrl: string;
}

interface RestaurantsSectionProps {
  restaurants: Restaurant[];
}

const RestaurantsSection: React.FC<RestaurantsSectionProps> = ({ restaurants }) => {
  return (
    <section className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Utensils className="w-6 h-6 text-primary-500" />
        Restaurants & Dining
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {restaurants.map((restaurant) => (
          <div key={restaurant.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            <img
              src={restaurant.imageUrl}
              alt={restaurant.name}
              className="w-full h-48 object-cover"
            />
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{restaurant.name}</h3>
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="ml-1 text-sm font-medium text-gray-600">{restaurant.rating}</span>
                </div>
              </div>

              <div className="flex items-center gap-4 mb-3">
                <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                  {restaurant.cuisine}
                </span>
                <div className="flex items-center text-gray-600">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <span
                      key={i}
                      className={`w-4 h-4 inline-block text-center ${
                        i < restaurant.priceRange.length ? 'text-gray-900' : 'text-gray-300'
                      }`}
                    >
                      ฿
                    </span>
                  ))}
                </div>
              </div>

              <p className="text-gray-600 text-sm italic">"{restaurant.reviewHighlight}"</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default RestaurantsSection;
