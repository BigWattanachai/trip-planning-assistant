import React from 'react';
import { Home, Star, Wifi, Coffee, Car, Bath, MapPin, Info, ExternalLink, Check } from 'lucide-react';
import { motion } from 'framer-motion';

interface Accommodation {
  id: string;
  name: string;
  type: string;
  rating: number;
  reviewCount: number;
  price: number;
  priceUnit: string;
  amenities: string[];
  imageUrl: string;
  platform: 'Airbnb' | 'Agoda' | 'TripAdvisor' | string;
  bookingUrl: string;
  location?: string;
  description?: string;
  distance?: string;
}

interface AccommodationSectionProps {
  accommodations: Accommodation[];
}

const amenityIcons: { [key: string]: React.ReactNode } = {
  'WiFi': <Wifi className="w-4 h-4" />,
  'Coffee': <Coffee className="w-4 h-4" />,
  'Parking': <Car className="w-4 h-4" />,
  'Private Bathroom': <Bath className="w-4 h-4" />,
};

const AccommodationSection: React.FC<AccommodationSectionProps> = ({ accommodations }) => {
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
        <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
          <Home className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Exceptional Stays
          </h2>
          <p className="text-gray-600">Carefully selected accommodations for your comfort and convenience</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {accommodations.map((accommodation, index) => (
          <motion.div 
            key={accommodation.id} 
            className="rounded-xl overflow-hidden border border-gray-200 bg-white hover:border-indigo-200 transition-all"
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            whileHover="hover"
            transition={{ delay: index * 0.1 }}
          >
            <div className="relative h-56 overflow-hidden">
              <img
                src={accommodation.imageUrl}
                alt={accommodation.name}
                className="w-full h-full object-cover transition-transform duration-700 hover:scale-110"
              />
              <div className="absolute top-4 right-4 bg-white bg-opacity-90 backdrop-blur-sm py-1 px-3 rounded-full">
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="ml-1 text-sm font-medium">{accommodation.rating}/5</span>
                  <span className="ml-1 text-xs text-gray-500">({accommodation.reviewCount})</span>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                <div className="inline-block bg-indigo-600 text-white text-xs px-2 py-1 rounded-md mb-2">
                  {accommodation.type}
                </div>
                <h3 className="text-xl font-bold text-white">{accommodation.name}</h3>
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <div className="text-xl font-bold text-indigo-600">฿{accommodation.price.toLocaleString()}</div>
                  <div className="text-sm text-gray-600 ml-1">/{accommodation.priceUnit}</div>
                </div>
                
                <div className="inline-flex items-center px-2 py-1 bg-gray-100 rounded text-sm text-gray-700">
                  via {accommodation.platform}
                </div>
              </div>
              
              {accommodation.description && (
                <div className="mb-4">
                  <p className="text-gray-700 text-sm">{accommodation.description}</p>
                </div>
              )}
              
              <div className="space-y-3 mb-4">
                {accommodation.location && (
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-2 text-indigo-500 flex-shrink-0" />
                    <span>{accommodation.location}</span>
                  </div>
                )}
                
                {accommodation.distance && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Info className="w-4 h-4 mr-2 text-indigo-500 flex-shrink-0" />
                    <span>{accommodation.distance} from city center</span>
                  </div>
                )}
              </div>
              
              <div className="mt-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Popular Amenities</h4>
                <div className="grid grid-cols-2 gap-2">
                  {accommodation.amenities.slice(0, 6).map((amenity, index) => (
                    <div key={index} className="flex items-center text-sm text-gray-700">
                      <Check className="w-4 h-4 mr-2 text-indigo-500" />
                      <span>{amenity}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="mt-5 pt-4 border-t border-gray-100">
                <a
                  href={accommodation.bookingUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                >
                  Book this stay
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {accommodations.length === 0 && (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No accommodations found. Your stay recommendations will appear here.</p>
        </div>
      )}
    </section>
  );
};

export default AccommodationSection;
