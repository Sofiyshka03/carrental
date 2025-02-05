import React from 'react';
import { Calendar, Shield, Star } from 'lucide-react';

export function Hero() {
  return (
    <div className="relative">
      <div className="absolute inset-0">
        <img
          className="w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1485291571150-772bcfc10da5?auto=format&fit=crop&q=80"
          alt="Luxury car"
        />
        <div className="absolute inset-0 bg-gray-900/70 mix-blend-multiply" />
      </div>
      
      <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Аренда премиальных автомобилей
        </h1>
        <p className="mt-6 max-w-3xl text-xl text-gray-300">
          Широкий выбор автомобилей премиум-класса для любых целей. Простое бронирование, 
          выгодные условия и превосходный сервис.
        </p>
        
        <div className="mt-10">
          <a
            href="/cars"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Выбрать автомобиль
          </a>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-3 lg:mt-24">
          {[
            {
              icon: Calendar,
              title: 'Быстрое бронирование',
              description: 'Оформление аренды за 15 минут',
            },
            {
              icon: Shield,
              title: 'Полная страховка',
              description: 'Все автомобили застрахованы',
            },
            {
              icon: Star,
              title: 'Премиум сервис',
              description: 'Индивидуальный подход к каждому клиенту',
            },
          ].map((feature) => (
            <div key={feature.title} className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
              <feature.icon className="h-8 w-8 text-blue-400" />
              <h3 className="mt-4 text-xl font-semibold text-white">{feature.title}</h3>
              <p className="mt-2 text-gray-300">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}