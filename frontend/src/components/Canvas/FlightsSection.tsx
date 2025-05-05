import React from 'react';
import { Plane, Clock, ArrowRight } from 'lucide-react';

interface Flight {
  id: string;
  airline: string;
  flightNumber: string;
  departure: {
    airport: string;
    time: string;
    date: string;
  };
  arrival: {
    airport: string;
    time: string;
    date: string;
  };
  duration: string;
  price: number;
  class: string;
  bookingUrl: string;
}

interface FlightsSectionProps {
  flights: Flight[];
}

const FlightsSection: React.FC<FlightsSectionProps> = ({ flights }) => {
  return (
    <section className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Plane className="w-6 h-6 text-primary-500" />
        Flight Options
      </h2>

      <div className="space-y-4">
        {flights.map((flight) => (
          <div key={flight.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{flight.airline}</h3>
                <p className="text-sm text-gray-600">Flight {flight.flightNumber}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">฿{flight.price}</div>
                <div className="text-sm text-gray-600">{flight.class}</div>
              </div>
            </div>

            <div className="flex items-center justify-between mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{flight.departure.time}</div>
                <div className="text-sm text-gray-600">{flight.departure.airport}</div>
                <div className="text-xs text-gray-500">{flight.departure.date}</div>
              </div>

              <div className="flex-1 mx-4">
                <div className="relative">
                  <div className="border-t-2 border-gray-300 w-full"></div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2">
                    <div className="flex items-center text-gray-600">
                      <Clock className="w-4 h-4 mr-1" />
                      <span className="text-sm">{flight.duration}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{flight.arrival.time}</div>
                <div className="text-sm text-gray-600">{flight.arrival.airport}</div>
                <div className="text-xs text-gray-500">{flight.arrival.date}</div>
              </div>
            </div>

            <div className="flex justify-end">
              <a
                href={flight.bookingUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2"
              >
                Book Flight
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default FlightsSection;
