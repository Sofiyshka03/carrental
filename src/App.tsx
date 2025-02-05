import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { CarCatalog } from './components/CarCatalog';
import { Services } from './components/Services';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route
            path="/"
            element={
              <main>
                <Hero />
                <Services />
              </main>
            }
          />
          <Route path="/cars" element={<CarCatalog />} />
          <Route path="/services" element={<Services />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;