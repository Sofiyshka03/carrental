import React, { useState } from 'react';
import { Filter, SortAsc } from 'lucide-react';
import { Car } from '../types';

const MOCK_CARS: Car[] = [
  {
    id: '1',
    brand: 'BMW',
    model: '7 Series',
    year: 2023,
    category: 'luxury',
    pricePerDay: 15000,
    images: ['https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&q=80'],
    available: true,
    specifications: {
      transmission: 'automatic',
      seats: 5,
      fuelType: 'Бензин',
      consumption: '8.5л/100км',
    },
  },
  {
    id: '2',
    brand: 'Mercedes-Benz',
    model: 'E-Class',
    year: 2023,
    category: 'business',
    pricePerDay: 12000,
    images: ['https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&q=80'],
    available: true,
    specifications: {
      transmission: 'automatic',
      seats: 5,
      fuelType: 'Бензин',
      consumption: '7.8л/100км',
    },
  },
  {
    id: '3',
    brand: 'Toyota',
    model: 'Camry',
    year: 2022,
    category: 'economy',
    pricePerDay: 5000,
    images: ['https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?auto=format&fit=crop&q=80'],
    available: true,
    specifications: {
      transmission: 'automatic',
      seats: 5,
      fuelType: 'Бензин',
      consumption: '6.5л/100км',
    },
  },
];

export function CarCatalog() {
  const [filters, setFilters] = useState({
    category: '',
    priceRange: '',
  });

  const filteredCars = MOCK_CARS.filter((car) => {
    if (filters.category && car.category !== filters.category) return false;
    if (filters.priceRange) {
      const [min, max] = filters.priceRange.split('-').map(Number);
      if (car.pricePerDay < min || car.pricePerDay > max) return false;
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Наш автопарк</h2>
        <div className="flex space-x-4">
          <select
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          >
            <option value="">Все категории</option>
            <option value="economy">Эконом</option>
            <option value="business">Бизнес</option>
            <option value="premium">Премиум</option>
            <option value="luxury">Люкс</option>
          </select>
          <select
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={filters.priceRange}
            onChange={(e) => setFilters({ ...filters, priceRange: e.target.value })}
          >
            <option value="">Любая цена</option>
            <option value="0-5000">До 5,000₽</option>
            <option value="5000-10000">5,000₽ - 10,000₽</option>
            <option value="10000-20000">10,000₽ - 20,000₽</option>
            <option value="20000-999999">Более 20,000₽</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredCars.map((car) => (
          <div key={car.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <img
              src={car.images[0]}
              alt={`${car.brand} ${car.model}`}
              className="w-full h-48 object-cover"
            />
            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-900">
                {car.brand} {car.model}
              </h3>
              <p className="mt-2 text-gray-600">{car.year} год</p>
              <div className="mt-4 flex justify-between items-center">
                <span className="text-2xl font-bold text-blue-600">
                  {car.pricePerDay.toLocaleString()}₽/день
                </span>
                <button
                  className={`px-4 py-2 rounded-md ${
                    car.available
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  disabled={!car.available}
                >
                  {car.available ? 'Забронировать' : 'Недоступно'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}