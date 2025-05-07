import React from 'react';
import { MapPin, Clock, Star, Camera, Calendar, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';

interface Activity {
  id: string;
  name: string;
  description: string;
  rating: number;
  openingHours: string;
  imageUrl: string;
  category: string;
  location?: string;
  price?: string;
  highlights?: string[];
  bestTimeToVisit?: string;
}

interface ActivitiesSectionProps {
  activities: Activity[];
}

const ActivitiesSection: React.FC<ActivitiesSectionProps> = ({ activities }) => {
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
        <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
          <MapPin className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Unforgettable Experiences
          </h2>
          <p className="text-gray-600">Discover handpicked attractions and activities for your journey</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            className="rounded-xl overflow-hidden border border-gray-200 bg-white hover:border-primary-200 transition-all"
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            whileHover="hover"
            transition={{ delay: index * 0.1 }}
          >
            <div className="relative h-56 overflow-hidden">
              <img
                src={activity.imageUrl}
                alt={activity.name}
                className="w-full h-full object-cover transition-transform duration-700 hover:scale-110"
              />
              <div className="absolute top-4 right-4 bg-white bg-opacity-90 backdrop-blur-sm py-1 px-3 rounded-full">
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="ml-1 text-sm font-medium">{activity.rating}/5</span>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                <div className="inline-block bg-primary-600 text-white text-xs px-2 py-1 rounded-md mb-2">
                  {activity.category}
                </div>
                <h3 className="text-xl font-bold text-white">{activity.name}</h3>
              </div>
            </div>
            
            <div className="p-6">
              <div className="prose prose-sm mb-4">
                <p className="text-gray-700 leading-relaxed">{activity.description}</p>
              </div>
              
              <div className="space-y-3 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
                  <span>{activity.openingHours}</span>
                </div>
                
                {activity.location && (
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
                    <span>{activity.location}</span>
                  </div>
                )}
                
                {activity.price && (
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="font-bold mr-2 text-primary-500 flex-shrink-0">฿</span>
                    <span>{activity.price}</span>
                  </div>
                )}
                
                {activity.bestTimeToVisit && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
                    <span>Best time: {activity.bestTimeToVisit}</span>
                  </div>
                )}
              </div>
              
              {activity.highlights && activity.highlights.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                    <Camera className="w-4 h-4 mr-1 text-primary-500" />
                    Highlights
                  </h4>
                  <ul className="space-y-1">
                    {activity.highlights.map((highlight, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start">
                        <span className="text-primary-500 mr-2">•</span>
                        {highlight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="mt-5 pt-4 border-t border-gray-100">
                <button className="text-primary-600 hover:text-primary-800 text-sm font-medium flex items-center transition-colors">
                  View full details
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {activities.length === 0 && (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No activities found. Your custom itinerary will appear here.</p>
        </div>
      )}
    </section>
  );
};

export default ActivitiesSection;
