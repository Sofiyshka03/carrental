<template>
  <div class="page-container">
    <h1 class="page-title">Наши автомобили</h1>
    <div class="content-section">
      <div class="filters-section">
        <div class="filter-group">
          <label>Год выпуска:</label>
          <div class="range-inputs">
            <input 
              type="number" 
              v-model="filters.yearFrom" 
              placeholder="От"
              min="1990"
              max="2030"
            >
            <input 
              type="number" 
              v-model="filters.yearTo" 
              placeholder="До"
              min="1990"
              max="2030"
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Категория:</label>
          <select v-model="filters.category" class="filter-select">
            <option value="">Все категории</option>
            <option value="Эконом">Эконом</option>
            <option value="Бизнес">Бизнес</option>
            <option value="Премиум">Премиум</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Цена (₽/день):</label>
          <div class="range-inputs">
            <input 
              type="number" 
              v-model="filters.priceFrom" 
              placeholder="От"
              min="0"
            >
            <input 
              type="number" 
              v-model="filters.priceTo" 
              placeholder="До"
              min="0"
            >
          </div>
        </div>
        
        <button @click="resetFilters" class="btn-reset">Сбросить фильтры</button>
      </div>

      <div v-if="loading" class="loading">
        Загрузка...
      </div>
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      <div v-else class="cars-grid">
        <div v-for="car in filteredCars" :key="car.ID_автомобиля" class="car-card">
          <!-- Отображаем iframe для Google Drive ссылок -->
          <iframe 
            v-if="getCarImage(car) && getCarImage(car).includes('/preview')"
            :src="getCarImage(car)"
            class="car-iframe"
            allowfullscreen
          ></iframe>
          <!-- Для обычных изображений используем img -->
          <img 
            v-else-if="getCarImage(car)"
            :src="getCarImage(car)"
            :alt="car.Марка + ' ' + car.Модель"
            @error="handleImageError"
            class="car-image"
          >
          <!-- Если нет изображения, показываем заглушку -->
          <div v-else class="car-placeholder">
            <span>{{ car.Марка }} {{ car.Модель }}</span>
          </div>
          <div class="car-info">
            <h3>{{ car.Марка }} {{ car.Модель }}</h3>
            <p>Год выпуска: {{ car.Год_выпуска }}</p>
            <p>Категория: {{ car.Категория }}</p>
            <p class="price">{{ car.Стоимость }} ₽/день</p>
            <button 
              v-if="isAuthenticated" 
              @click="bookCar(car)" 
              :disabled="car.Статус_авто !== 'Доступен'"
              :class="{ 'disabled': car.Статус_авто !== 'Доступен' }"
            >
              {{ car.Статус_авто === 'Доступен' ? 'Забронировать' : 'Недоступен' }}
            </button>
            <router-link 
              v-else 
              to="/login" 
              class="login-link"
            >
              Войдите для бронирования
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CarList',
  data() {
    return {
      cars: [],
      loading: true,
      error: null,
      filters: {
        yearFrom: '',
        yearTo: '',
        category: '',
        priceFrom: '',
        priceTo: ''
      }
    }
  },
  computed: {
    isAuthenticated() {
      return this.$store.state.auth.isAuthenticated
    },
    filteredCars() {
      return this.cars.filter(car => {
        if (car.Статус_авто !== 'Доступен') return false
        
        if (this.filters.yearFrom && car.Год_выпуска < this.filters.yearFrom) return false
        if (this.filters.yearTo && car.Год_выпуска > this.filters.yearTo) return false
        
        if (this.filters.category && car.Категория !== this.filters.category) return false
        
        if (this.filters.priceFrom && car.Стоимость < this.filters.priceFrom) return false
        if (this.filters.priceTo && car.Стоимость > this.filters.priceTo) return false
        
        return true
      })
    }
  },
  methods: {
    async fetchCars() {
      try {
        this.loading = true
        const response = await this.$axios.get('/api/cars')
        this.cars = response.data
        this.error = null
      } catch (error) {
        console.error('Ошибка при загрузке автомобилей:', error)
        this.error = 'Ошибка при загрузке списка автомобилей'
      } finally {
        this.loading = false
      }
    },
    bookCar(car) {
      this.$router.push(`/booking/${car.ID_автомобиля}`)
    },
    getCarImage(car) {
      // Если у автомобиля нет изображения, используем плейсхолдер
      if (!car.image) {
        return null;
      }
      
      // Для ссылок Google Drive используем прямой формат для встраивания
      if (car.image.includes('drive.google.com/file/d/')) {
        const idMatch = car.image.match(/\/file\/d\/([^\/]+)\//)
        if (idMatch && idMatch[1]) {
          const fileId = idMatch[1]
          // Возвращаем прямую ссылку для <iframe> вместо <img>
          return `https://drive.google.com/file/d/${fileId}/preview`
        }
      }
      
      return car.image
    },
    handleImageError(e) {
      // Скрываем изображение при ошибке, чтобы не показывался плейсхолдер
      e.target.style.display = 'none';
    },
    resetFilters() {
      this.filters = {
        yearFrom: '',
        yearTo: '',
        category: '',
        priceFrom: '',
        priceTo: ''
      }
    }
  },
  mounted() {
    this.fetchCars()
  }
}
</script>

<style scoped>
.cars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.car-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.car-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 255, 157, 0.3);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.car-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.car-info {
  padding: 1rem 0;
}

.car-info h3 {
  color: rgb(66, 185, 131);
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
}

.car-info p {
  color: #ffffff;
  opacity: 0.8;
  margin: 0.5rem 0;
}

.price {
  font-size: 1.25rem;
  font-weight: bold;
  color: rgb(66, 185, 131);
  margin: 1rem 0;
}

button {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(135deg, #0066ff 0%, rgb(66, 185, 131) 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
}

button.disabled {
  background: #4a4a4a;
  cursor: not-allowed;
  transform: none;
}

.login-link {
  display: block;
  text-align: center;
  color: rgb(66, 185, 131);
  text-decoration: none;
  margin-top: 1rem;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.login-link:hover {
  opacity: 1;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #dc3545;
}

.car-placeholder {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #2a2a2a 0%, #3d3d3d 100%);
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgb(66, 185, 131);
  font-size: 1.5rem;
  font-weight: bold;
}

.car-iframe {
  width: 100%;
  height: 200px;
  border: none;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.car-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.filters-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  color: rgb(66, 185, 131);
  font-size: 1rem;
}

.range-inputs {
  display: flex;
  gap: 0.5rem;
}

.range-inputs input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.filter-select {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.5rem;
  width: 100%;
  outline: none;
}

.filter-select option {
  color: #000000;
  background-color: #ffffff;
}

.btn-reset {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-reset:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style> 