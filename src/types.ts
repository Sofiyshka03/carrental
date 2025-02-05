export interface Car {
  id: string;
  brand: string;
  model: string;
  year: number;
  category: 'economy' | 'business' | 'premium' | 'luxury';
  pricePerDay: number;
  images: string[];
  available: boolean;
  specifications: {
    transmission: 'automatic' | 'manual';
    seats: number;
    fuelType: string;
    consumption: string;
  };
}

export interface NavigationItem {
  label: string;
  href: string;
  icon?: React.ComponentType;
}