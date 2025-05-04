import React, { useState } from 'react';
import { MapPin, CalendarDays, DollarSign } from 'lucide-react';

interface TripInputFormProps {
  onSubmit: (data: TripInput) => void;
}

interface TripInput {
  departure: string;
  destination: string;
  startDate: string;
  endDate: string;
  budgetRange: string;
}

const TripInputForm: React.FC<TripInputFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<TripInput>({
    departure: '',
    destination: '',
    startDate: '',
    endDate: '',
    budgetRange: 'medium',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg border border-gray-200 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Departure Location
            </div>
          </label>
          <input
            type="text"
            name="departure"
            value={formData.departure}
            onChange={handleChange}
            placeholder="e.g., San Francisco"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Destination
            </div>
          </label>
          <input
            type="text"
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            placeholder="e.g., Bangkok"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <div className="flex items-center gap-2">
              <CalendarDays className="w-4 h-4" />
              Start Date
            </div>
          </label>
          <input
            type="date"
            name="startDate"
            value={formData.startDate}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <div className="flex items-center gap-2">
              <CalendarDays className="w-4 h-4" />
              End Date
            </div>
          </label>
          <input
            type="date"
            name="endDate"
            value={formData.endDate}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Budget Range (THB)
          </div>
        </label>
        <select
          name="budgetRange"
          value={formData.budgetRange}
          onChange={handleChange}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="budget">Budget (฿ - Under ฿35,000)</option>
          <option value="medium">Medium (฿฿ - ฿35,000-฿105,000)</option>
          <option value="luxury">Luxury (฿฿฿ - Above ฿105,000)</option>
        </select>
      </div>

      <button
        type="submit"
        className="w-full bg-primary-500 text-white py-2 px-4 rounded-lg hover:bg-primary-600 transition-colors font-medium"
      >
        Plan My Trip
      </button>
    </form>
  );
};

export default TripInputForm;
