<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>CarRental</h1>
      <p class="tagline">Ваш надежный партнер в аренде автомобилей</p>
      <div class="hero-overlay"></div>
    </div>
    
    <div class="features-section">
      <div class="features-content">
        <div class="section-group">
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">
                <i class="fas fa-car"></i>
              </div>
              <h3>Новый автопарк</h3>
              <p>Современные автомобили в идеальном состоянии</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">
                <i class="fas fa-file-contract"></i>
              </div>
              <h3>Гибкие условия</h3>
              <p>Индивидуальный подход к каждому клиенту</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">
                <i class="fas fa-headset"></i>
              </div>
              <h3>Поддержка 24/7</h3>
              <p>Техническая поддержка в любое время суток</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <h3>Страхование</h3>
              <p>Полное страхование всех автомобилей</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="about-section">
      <h2>О нас</h2>
      <div class="content">
        <div class="about-text">
          <p>
            CarRental – ваш надежный партнер в сфере аренды автомобилей. 
            Мы специализируемся на предоставлении качественных автомобилей различных классов 
            для любых целей: от деловых поездок до семейных путешествий.
          </p>
          <p>
            Наш автопарк регулярно обновляется, а каждый автомобиль проходит тщательное 
            техническое обслуживание. Мы гарантируем прозрачные условия аренды и 
            индивидуальный подход к каждому клиенту.
          </p>
        </div>
        <div class="contact-info">
          <h3>Контактная информация</h3>
          <div class="contact-grid">
            <div class="contact-item">
              <div class="contact-icon">
                <i class="fas fa-phone"></i>
              </div>
              <div class="contact-text">
                <h4>Телефон</h4>
                <p>+7 (495) 123-45-67</p>
              </div>
            </div>
            <div class="contact-item">
              <div class="contact-icon">
                <i class="fas fa-envelope"></i>
              </div>
              <div class="contact-text">
                <h4>Email</h4>
                <p>info@car-rental.ru</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #1a1a1a;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>

<style scoped>
.home-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0;
  background-color: #1a1a1a;
  color: #ffffff;
  min-height: 100vh;
}

.hero-section {
  text-align: center;
  padding: 6rem 0;
  background: url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&q=80') center/cover;
  color: white;
  border-radius: 0;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(0, 102, 255, 0.8), rgba(0, 255, 157, 0.8));
  z-index: 1;
}

.hero-section h1 {
  font-size: 4rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 2;
  text-transform: uppercase;
  letter-spacing: 3px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.tagline {
  font-size: 1.8rem;
  opacity: 0.9;
  position: relative;
  z-index: 2;
  font-weight: 300;
}

.features-section {
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  padding: 5rem 0;
}

.features-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-group {
  margin-bottom: 5rem;
}

.section-group:last-child {
  margin-bottom: 0;
}

.section-group h2 {
  text-align: center;
  color: rgb(66, 185, 131);
  font-size: 2.5rem;
  margin-bottom: 3rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
}

.section-group h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: #0066ff;
  border-radius: 2px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(0, 255, 157, 0.1), transparent);
  transform: translateX(-100%);
  transition: 0.5s;
}

.feature-card:hover::before {
  transform: translateX(100%);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  border-color: rgba(0, 255, 157, 0.3);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #0066ff 0%, #00ff9d 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 6s ease-in-out infinite;
}

.feature-icon i {
  font-size: 2rem;
  color: white;
}

.feature-card h3 {
  color: rgb(66, 185, 131);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #ffffff;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1.1rem;
}

.about-section {
  background: #2a2a2a;
  padding: 2rem;
  border-radius: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.about-section h2 {
  color: rgb(66, 185, 131);
  font-size: 2rem;
  margin-bottom: 1rem;
  text-align: center;
  position: relative;
}

.content {
  display: grid;
  align-items: center;
 
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.about-text {
  color: #ffffff;
  opacity: 0.8;
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.about-text p {
  margin-bottom: 1rem;
}

.about-text p:last-child {
  margin-bottom: 2rem;
}

.contact-info {
  background: #333333;
  padding: 0 2rem 2rem 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.contact-info h3 {
  margin-bottom: 2rem;
  color: rgb(66, 185, 131);
  font-size: 1.5rem;
  text-align: center;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.contact-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.1);
}

.contact-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0066ff 0%, #00ff9d 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contact-icon i {
  font-size: 1.2rem;
  color: white;
}

.contact-text h4 {
  color: rgb(66, 185, 131);
  margin: 0 0 0.2rem 0;
  font-size: 0.9rem;
  font-weight: 500;
}

.contact-text p {
  color: #ffffff;
  opacity: 0.8;
  margin: 0;
  font-size: 0.95rem;
}

.contact-item {
  padding: 0.8rem;
}

.contact-icon {
  width: 35px;
  height: 35px;
}

@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
    width: 100%;
  }

  .nav-button {
    width: 100%;
  }

  .content {
    grid-template-columns: 1fr;
    padding: 0 1rem;
  }
  
  .hero-section {
    padding: 4rem 1rem;
  }
  
  .hero-section h1 {
    font-size: 3rem;
  }
  
  .tagline {
    font-size: 1.4rem;
  }

  .features-content {
    padding: 0 1rem;
  }

  .feature-card {
    padding: 1.5rem;
  }

  .feature-icon {
    width: 60px;
    height: 60px;
  }

  .feature-icon i {
    font-size: 1.5rem;
  }

  .contact-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .contact-info {
    padding: 1.5rem;
  }

  .contact-item {
    padding: 0.8rem;
  }
}
</style>