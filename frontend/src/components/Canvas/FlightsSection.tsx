import React from 'react';
import { Plane, Clock, ArrowRight, Calendar, Luggage, Shield, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';

interface Flight {
  id: string;
  airline: string;
  flightNumber: string;
  departure: {
    airport: string;
    time: string;
    date: string;
    terminal?: string;
  };
  arrival: {
    airport: string;
    time: string;
    date: string;
    terminal?: string;
  };
  duration: string;
  price: number;
  class: string;
  bookingUrl: string;
  stops?: number;
  layover?: string;
  amenities?: string[];
  cancellationPolicy?: string;
  airlineLogoUrl?: string;
}

interface FlightsSectionProps {
  flights: Flight[];
}

const FlightsSection: React.FC<FlightsSectionProps> = ({ flights }) => {
  return (
    <section className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center">
          <Plane className="w-6 h-6 text-teal-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Seamless Sky Travel
          </h2>
          <p className="text-gray-600">Optimal flight options for your journey based on your preferences</p>
        </div>
      </div>

      <div className="space-y-6">
        {flights.map((flight, index) => (
          <motion.div 
            key={flight.id} 
            className="border border-gray-200 rounded-xl overflow-hidden hover:border-teal-200 transition-all bg-white"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            whileHover={{
              y: -5,
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
              transition: { duration: 0.3 }
            }}
          >
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                  {flight.airlineLogoUrl ? (
                    <img 
                      src={flight.airlineLogoUrl} 
                      alt={flight.airline} 
                      className="w-10 h-10 object-contain" 
                    />
                  ) : (
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      <Plane className="w-5 h-5 text-gray-600" />
                    </div>
                  )}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{flight.airline}</h3>
                    <p className="text-sm text-gray-600">Flight {flight.flightNumber}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-teal-600">฿{flight.price.toLocaleString()}</div>
                  <div className="inline-block px-2 py-1 bg-teal-50 text-teal-800 text-xs rounded">
                    {flight.class}
                  </div>
                </div>
              </div>

              <div className="flex flex-col md:flex-row items-stretch justify-between mb-6 bg-gray-50 rounded-xl overflow-hidden">
                <div className="p-4 md:p-6 flex-1 border-r border-gray-200">
                  <div className="text-xs uppercase text-gray-500 mb-1">Departure</div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">{flight.departure.time}</div>
                  <div className="text-sm text-gray-700 font-medium">{flight.departure.airport}</div>
                  <div className="flex items-center text-xs text-gray-500 mt-2">
                    <Calendar className="w-3 h-3 mr-1" />
                    {flight.departure.date}
                  </div>
                  {flight.departure.terminal && (
                    <div className="text-xs text-gray-500 mt-1">
                      Terminal: {flight.departure.terminal}
                    </div>
                  )}
                </div>

                <div className="py-4 px-6 flex flex-col justify-center items-center">
                  <div className="flex items-center text-gray-600 mb-2">
                    <Clock className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">{flight.duration}</span>
                  </div>
                  
                  <div className="relative w-32 md:w-40 h-6 my-2">
                    <div className="absolute top-1/2 left-0 right-0 border-t-2 border-dashed border-gray-300 transform -translate-y-1/2"></div>
                    <div className="absolute top-1/2 left-0 w-3 h-3 bg-teal-500 rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
                    <div className="absolute top-1/2 right-0 w-3 h-3 bg-teal-700 rounded-full transform translate-x-1/2 -translate-y-1/2"></div>
                    {flight.stops && flight.stops > 0 && (
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                        <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-bold">{flight.stops}</span>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {flight.stops && flight.stops > 0 ? (
                    <div className="text-xs text-amber-600 font-medium flex items-center">
                      {flight.stops} stop{flight.stops > 1 ? 's' : ''}
                      {flight.layover && <span className="ml-1">• {flight.layover} layover</span>}
                    </div>
                  ) : (
                    <div className="text-xs text-teal-600 font-medium">Direct flight</div>
                  )}
                </div>

                <div className="p-4 md:p-6 flex-1 border-l border-gray-200">
                  <div className="text-xs uppercase text-gray-500 mb-1">Arrival</div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">{flight.arrival.time}</div>
                  <div className="text-sm text-gray-700 font-medium">{flight.arrival.airport}</div>
                  <div className="flex items-center text-xs text-gray-500 mt-2">
                    <Calendar className="w-3 h-3 mr-1" />
                    {flight.arrival.date}
                  </div>
                  {flight.arrival.terminal && (
                    <div className="text-xs text-gray-500 mt-1">
                      Terminal: {flight.arrival.terminal}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col-reverse md:flex-row justify-between items-center">
                <div className="w-full md:w-auto mt-4 md:mt-0">
                  {flight.amenities && flight.amenities.length > 0 && (
                    <div className="flex flex-wrap gap-2 items-center">
                      <span className="text-xs text-gray-500">Amenities:</span>
                      {flight.amenities.map((amenity, idx) => (
                        <span 
                          key={idx} 
                          className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                        >
                          {amenity}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {flight.cancellationPolicy && (
                    <div className="flex items-center mt-2 text-xs text-gray-600">
                      <Shield className="w-3 h-3 mr-1 text-teal-500" />
                      {flight.cancellationPolicy}
                    </div>
                  )}
                </div>
                
                <a
                  href={flight.bookingUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors text-sm font-medium"
                >
                  Book this flight
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {flights.length === 0 && (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No flights found. Your flight options will appear here.</p>
        </div>
      )}
    </section>
  );
};

export default FlightsSection;
