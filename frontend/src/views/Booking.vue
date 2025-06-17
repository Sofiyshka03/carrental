<template>
  <div class="page-container">
    <h1 class="page-title">Бронирование автомобиля</h1>
    
    <div class="content-section">
      <div v-if="loading" class="loading">
        Загрузка...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="car" class="booking-form">
        <div class="car-details">
          <!-- Используем iframe для Google Drive ссылок -->
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
          <h3>{{ car.Марка }} {{ car.Модель }}</h3>
          <p class="car-price">{{ car.Стоимость }} ₽ в день</p>
        </div>
        
        <form @submit.prevent="createBooking">
          <div class="form-group">
            <label class="form-label">Дата начала</label>
            <input v-model="form.start_date" type="date" class="form-input" :min="minDate" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Дата окончания</label>
            <input v-model="form.end_date" type="date" class="form-input" :min="form.start_date" required>
          </div>
          
          <!-- Дополнительные услуги -->
          <div class="services-section">
            <h3>Дополнительные услуги</h3>
            <div v-for="service in services" :key="service.id" class="service-item">
              <div class="service-checkbox">
                <input 
                  type="checkbox" 
                  :id="'service-' + service.id"
                  :value="service"
                  v-model="selectedServices"
                  @change="updateServices"
                >
                <label :for="'service-' + service.id">
                  {{ service.name }} ({{ service.cost }} ₽)
                </label>
              </div>
              
              <div v-if="isServiceSelected(service)" class="quantity-control">
                <button 
                  @click="decreaseQuantity(service.id)"
                  class="quantity-btn"
                  :disabled="getServiceQuantity(service.id) <= 1"
                >-</button>
                <input 
                  type="number" 
                  :value="getServiceQuantity(service.id)"
                  @input="updateQuantity(service.id, $event.target.value)"
                  min="1"
                  class="quantity-input"
                >
                <button 
                  @click="increaseQuantity(service.id)"
                  class="quantity-btn"
                >+</button>
              </div>
            </div>
          </div>
          
          <!-- Способ оплаты -->
          <div class="form-group">
            <label class="form-label">Способ оплаты</label>
            <select v-model="form.payment_method" class="form-input" required>
              <option value="Карта">Банковская карта</option>
              <option value="Наличные">Наличные</option>
            </select>
          </div>
          
          <div class="total-cost" v-if="totalCost">
            <div class="cost-item">
              <span>Стоимость аренды:</span>
              <span>{{ rentalCost }} ₽</span>
            </div>
            <div class="cost-item">
              <span>Стоимость доп. услуг:</span>
              <span>{{ servicesCost }} ₽</span>
            </div>
            <div class="cost-item total">
              <span>Итого к оплате:</span>
              <span>{{ totalCost }} ₽</span>
            </div>
          </div>
          
          <button type="submit" class="btn" :disabled="loading || !isFormValid">
            {{ loading ? 'Создание бронирования...' : 'Забронировать' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Booking',
  data() {
    return {
      car: null,
      services: [],
      selectedServices: [],
      form: {
        start_date: '',
        end_date: '',
        services: [],
        payment_method: 'Карта'
      },
      loading: false,
      error: null,
      serviceQuantities: {}
    }
  },
  computed: {
    minDate() {
      const today = new Date()
      return today.toISOString().split('T')[0]
    },
    rentalCost() {
      if (!this.car || !this.form.start_date || !this.form.end_date) return 0
      const start = new Date(this.form.start_date)
      const end = new Date(this.form.end_date)
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
      return this.car.Стоимость * days
    },
    servicesCost() {
      return this.selectedServices.reduce((total, service) => {
        const quantity = this.serviceQuantities[service.id] || 1;
        return total + (service.cost * quantity);
      }, 0);
    },
    totalCost() {
      return this.rentalCost + this.servicesCost;
    },
    isFormValid() {
      return this.form.start_date && 
             this.form.end_date && 
             this.form.payment_method &&
             !this.loading
    }
  },
  methods: {
    isServiceSelected(service) {
      return this.selectedServices.includes(service)
    },
    getServiceQuantity(serviceId) {
      return this.serviceQuantities[serviceId] || 1
    },
    increaseQuantity(serviceId) {
      const currentQuantity = this.getServiceQuantity(serviceId)
      this.serviceQuantities[serviceId] = currentQuantity + 1
      this.updateServices()
    },
    decreaseQuantity(serviceId) {
      const currentQuantity = this.getServiceQuantity(serviceId)
      if (currentQuantity > 1) {
        this.serviceQuantities[serviceId] = currentQuantity - 1
        this.updateServices()
      }
    },
    updateQuantity(serviceId, value) {
      const quantity = parseInt(value)
      if (!isNaN(quantity) && quantity > 0) {
        this.serviceQuantities[serviceId] = quantity
        this.updateServices()
      }
    },
    updateServices() {
      this.form.services = this.selectedServices.map(service => ({
        id: service.id,
        quantity: this.getServiceQuantity(service.id)
      }))
    },
    async fetchCar() {
      this.loading = true
      try {
        const response = await this.$axios.get(`/api/cars/${this.$route.params.id}`)
        this.car = response.data
        console.log('Загруженный автомобиль:', this.car)
      } catch (error) {
        console.error('Ошибка при загрузке автомобиля:', error)
        this.error = 'Ошибка при загрузке данных автомобиля'
      } finally {
        this.loading = false
      }
    },
    async fetchServices() {
      try {
        const response = await this.$axios.get('/api/services')
        this.services = response.data
        console.log('Загруженные услуги:', this.services)
      } catch (error) {
        console.error('Ошибка при загрузке услуг:', error)
        this.error = 'Ошибка при загрузке дополнительных услуг'
      }
    },
    async createBooking() {
      if (!this.$store.state.auth.isAuthenticated) {
        this.error = 'Необходимо войти в систему'
        return
      }
      this.loading = true
      this.error = null
      
      if (!this.form.start_date || !this.form.end_date || !this.form.payment_method) {
        this.error = 'Пожалуйста, заполните все обязательные поля'
        this.loading = false
        return
      }
      
      const bookingData = {
        car_id: this.car.ID_автомобиля,
        start_date: this.form.start_date,
        end_date: this.form.end_date,
        payment_method: this.form.payment_method,
        services: this.selectedServices.map(service => ({
          id: service.id,
          quantity: this.serviceQuantities[service.id] || 1
        }))
      }
      
      console.log('Отправляемые данные:', JSON.stringify(bookingData, null, 2))
      
      try {
        const response = await this.$axios.post('/api/bookings', bookingData)
        console.log('Ответ сервера:', response.data)
        this.$router.push('/profile')
      } catch (error) {
        console.error('Ошибка при бронировании:', error.response?.data || error)
        this.error = error.response?.data?.error || 'Ошибка при создании бронирования'
      } finally {
        this.loading = false
      }
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
    }
  },
  async mounted() {
    if (!this.$store.state.auth.isAuthenticated) {
      this.$router.push('/login')
      return
    }
    await this.fetchCar()
    await this.fetchServices()
  }
}
</script>

<style scoped>
.car-details {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.car-details h3 {
  color: rgb(66, 185, 131);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.car-price {
  font-size: 1.2rem;
  color: #ffffff;
  opacity: 0.8;
}

.services-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 10px;
  margin: 1.5rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.services-section h3 {
  color: rgb(66, 185, 131);
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.service-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.service-checkbox {
  display: flex;
  align-items: center;
}

.service-checkbox input[type="checkbox"] {
  margin-right: 0.8rem;
  cursor: pointer;
}

.service-checkbox label {
  cursor: pointer;
  color: #ffffff;
  opacity: 0.9;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-btn {
  width: 30px;
  height: 30px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.quantity-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-input {
  width: 60px;
  text-align: center;
  padding: 0.3rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.total-cost {
  background: rgba(0, 255, 157, 0.1);
  padding: 1.5rem;
  border-radius: 10px;
  margin: 1.5rem 0;
  border: 1px solid rgba(66, 185, 131, 0.3);
}

.cost-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #ffffff;
  opacity: 0.8;
}

.cost-item.total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: bold;
  font-size: 1.2rem;
  color: rgb(66, 185, 131);
  opacity: 1;
}

.car-image {
  width: 100%;
  max-width: 300px;
  height: 160px;
  object-fit: cover;
  border-radius: 10px;
  margin: 0 auto 1rem;
  display: block;
}

.car-iframe {
  width: 100%;
  max-width: 300px;
  height: 160px;
  border-radius: 10px;
  margin: 0 auto 1rem;
  display: block;
}

.car-placeholder {
  width: 100%;
  max-width: 300px;
  height: 160px;
  border-radius: 10px;
  margin: 0 auto 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.05);
}

.car-placeholder span {
  color: #ffffff;
  opacity: 0.8;
}
</style> 