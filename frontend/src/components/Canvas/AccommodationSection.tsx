import React from 'react';
import { Home, Star, Wifi, Coffee, Car, Bath } from 'lucide-react';

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
  platform: 'Airbnb' | 'Agoda' | 'TripAdvisor';
  bookingUrl: string;
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
  return (
    <section className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Home className="w-6 h-6 text-primary-500" />
        Accommodations
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {accommodations.map((accommodation) => (
          <div key={accommodation.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            <img
              src={accommodation.imageUrl}
              alt={accommodation.name}
              className="w-full h-48 object-cover"
            />
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{accommodation.name}</h3>
                  <p className="text-sm text-gray-600">{accommodation.type}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-600">฿{accommodation.price}</div>
                  <div className="text-sm text-gray-600">/{accommodation.priceUnit}</div>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="ml-1 text-sm font-medium text-gray-900">{accommodation.rating}</span>
                </div>
                <span className="text-sm text-gray-600">({accommodation.reviewCount} reviews)</span>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {accommodation.amenities.slice(0, 4).map((amenity, index) => (
                  <div key={index} className="flex items-center gap-1 bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                    {amenityIcons[amenity] || <Home className="w-3 h-3" />}
                    <span>{amenity}</span>
                  </div>
                ))}
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-600">via {accommodation.platform}</span>
                <a
                  href={accommodation.bookingUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors text-sm"
                >
                  View Details
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default AccommodationSection;
