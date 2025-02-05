import React from 'react';
import { Link } from 'react-router-dom';
import { Car, ShieldCheck, User } from 'lucide-react';
import { NavigationItem } from '../types';

const navigation: NavigationItem[] = [
  { label: 'Автомобили', href: '/cars', icon: Car },
  { label: 'Услуги', href: '/services', icon: ShieldCheck },
  { label: 'Личный кабинет', href: '/account', icon: User },
];

export function Header() {
  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <Car className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">AutoRent</span>
            </Link>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600"
              >
                {item.icon && <item.icon className="h-4 w-4 mr-2" />}
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
    </header>
  );
}