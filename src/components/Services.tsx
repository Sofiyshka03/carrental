import React from 'react';
import { Shield, Car, Clock, MapPin, Headphones, PenTool as Tool, CreditCard, Users } from 'lucide-react';

const services = [
  {
    icon: Shield,
    title: 'Страхование',
    description: 'Полное КАСКО для всех автомобилей',
  },
  {
    icon: Clock,
    title: 'Круглосуточная аренда',
    description: 'Доступно 24/7 с поддержкой',
  },
  {
    icon: MapPin,
    title: 'Доставка автомобиля',
    description: 'Привезем машину в удобное место',
  },
  {
    icon: Headphones,
    title: 'Поддержка 24/7',
    description: 'Всегда на связи',
  },
  {
    icon: Tool,
    title: 'Техническое обслуживание',
    description: 'Регулярные проверки и ТО',
  },
  {
    icon: CreditCard,
    title: 'Удобная оплата',
    description: 'Принимаем все виды карт',
  },
];

export function Services() {
  return (
    <div className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">Наши услуги</h2>
          <p className="mt-4 text-xl text-gray-600">
            Мы предлагаем полный спектр услуг для комфортной аренды автомобиля
          </p>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <div
              key={service.title}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-600 ring-4 ring-white">
                  <service.icon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <a href="#" className="focus:outline-none">
                    <span className="absolute inset-0" aria-hidden="true" />
                    {service.title}
                  </a>
                </h3>
                <p className="mt-2 text-sm text-gray-500">{service.description}</p>
              </div>
              <span
                className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                aria-hidden="true"
              >
                <svg
                  className="h-6 w-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                </svg>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}