import React from 'react';
import { Utensils, Star, DollarSign, MapPin, Clock, ExternalLink, ThumbsUp } from 'lucide-react';
import { motion } from 'framer-motion';

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  priceRange: string;
  rating: number;
  reviewHighlight: string;
  imageUrl: string;
  location?: string;
  hours?: string;
  specialties?: string[];
  reservationRequired?: boolean;
}

interface RestaurantsSectionProps {
  restaurants: Restaurant[];
}

const RestaurantsSection: React.FC<RestaurantsSectionProps> = ({ restaurants }) => {
  // Animation variants
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    },
    hover: {
      y: -10,
      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
      transition: { duration: 0.3 }
    }
  };

  return (
    <section className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
          <Utensils className="w-6 h-6 text-amber-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Culinary Discoveries
          </h2>
          <p className="text-gray-600">Extraordinary dining experiences tailored to your tastes</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {restaurants.map((restaurant, index) => (
          <motion.div
            key={restaurant.id}
            className="rounded-xl overflow-hidden border border-gray-200 bg-white hover:border-amber-200 transition-all"
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            whileHover="hover"
            transition={{ delay: index * 0.1 }}
          >
            <div className="relative h-56 overflow-hidden">
              <img
                src={restaurant.imageUrl}
                alt={restaurant.name}
                className="w-full h-full object-cover transition-transform duration-700 hover:scale-110"
              />
              <div className="absolute top-4 right-4 bg-white bg-opacity-90 backdrop-blur-sm py-1 px-3 rounded-full">
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="ml-1 text-sm font-medium">{restaurant.rating}/5</span>
                </div>
              </div>
              {restaurant.reservationRequired && (
                <div className="absolute top-4 left-4 bg-red-500 text-white text-xs py-1 px-3 rounded-full">
                  Reservation Required
                </div>
              )}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                <div className="inline-block bg-amber-600 text-white text-xs px-2 py-1 rounded-md mb-2">
                  {restaurant.cuisine}
                </div>
                <h3 className="text-xl font-bold text-white">{restaurant.name}</h3>
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex text-amber-600">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <span
                      key={i}
                      className={`w-6 h-6 inline-flex items-center justify-center ${
                        i < restaurant.priceRange.length ? 'opacity-100' : 'opacity-30'
                      }`}
                    >
                      ฿
                    </span>
                  ))}
                </div>
                
                {restaurant.location && (
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-1 text-amber-500" />
                    <span>{restaurant.location}</span>
                  </div>
                )}
              </div>
              
              <div className="bg-amber-50 p-4 rounded-lg mb-4 relative">
                <ThumbsUp className="w-5 h-5 text-amber-500 absolute top-3 left-3" />
                <p className="text-gray-700 text-sm italic pl-8 pr-2">"{restaurant.reviewHighlight}"</p>
              </div>
              
              <div className="space-y-3">
                {restaurant.hours && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="w-4 h-4 mr-2 text-amber-500 flex-shrink-0" />
                    <span>{restaurant.hours}</span>
                  </div>
                )}
                
                {restaurant.specialties && restaurant.specialties.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Signature Dishes:</h4>
                    <div className="flex flex-wrap gap-2">
                      {restaurant.specialties.map((specialty, idx) => (
                        <span 
                          key={idx} 
                          className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full"
                        >
                          {specialty}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="mt-5 pt-4 border-t border-gray-100">
                <button className="text-amber-600 hover:text-amber-800 text-sm font-medium flex items-center transition-colors">
                  See menu and reviews
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {restaurants.length === 0 && (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No restaurants found. Your dining recommendations will appear here.</p>
        </div>
      )}
    </section>
  );
};

export default RestaurantsSection;
