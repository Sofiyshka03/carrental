<template>
  <div class="page-container">
    <h1 class="page-title">Личный кабинет</h1>
    <div class="content-section">
      <div class="profile-content">
        <div v-if="loading" class="loading">
          Загрузка...
        </div>
        
        <div v-else-if="error" class="error">
          {{ error }}
        </div>
        
        <div v-else>
          <!-- Бронирования -->
          <div v-if="bookings.length" class="bookings-list">
            <h3>Ваши бронирования</h3>
            <div v-for="booking in bookings" :key="booking.ID_договора" class="booking-card">
              <div class="booking-details-flex">
                <div class="car-image-container" v-if="booking.Автомобиль">
                  <template v-if="getCarImage(booking.Автомобиль) && getCarImage(booking.Автомобиль).includes('/preview')">
                    <iframe 
                      :src="getCarImage(booking.Автомобиль)"
                      class="car-image"
                      allowfullscreen
                    ></iframe>
                  </template>
                  <template v-else-if="getCarImage(booking.Автомобиль)">
                    <img 
                      :src="getCarImage(booking.Автомобиль)"
                      :alt="booking.Автомобиль.Марка + ' ' + booking.Автомобиль.Модель"
                      class="car-image"
                    >
                  </template>
                  <div v-else class="car-placeholder">
                    {{ booking.Автомобиль.Марка }} {{ booking.Автомобиль.Модель }}
                  </div>
                </div>
                <div class="booking-info">
                  <h4 v-if="booking.Автомобиль">{{ booking.Автомобиль.Марка }} {{ booking.Автомобиль.Модель }}</h4>
                  <p>Дата начала: {{ formatDate(booking.Дата_начала) }}</p>
                  <p>Дата окончания: {{ formatDate(booking.Дата_окончания) }}</p>
                  <p>Статус: {{ booking.Статус_договора }}</p>
                  <p>Стоимость: {{ booking.Стоимость }} ₽</p>
                  <button 
                    v-if="canCancelBooking(booking)"
                    @click="cancelBooking(booking.ID_договора)"
                    class="btn-cancel"
                  >
                    Отменить бронирование
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-bookings">
            <p>У вас пока нет бронирований</p>
          </div>
          
          <!-- Штрафы -->
          <div class="fines-section">
            <h3>Ваши штрафы</h3>
            <div v-if="loadingFines" class="loading">
              Загрузка штрафов...
            </div>
            <div v-else-if="finesError" class="error">
              {{ finesError }}
            </div>
            <div v-else-if="fines.length" class="fines-list">
              <div v-for="fine in fines" :key="fine.Название + fine.Стоимость + fine.Количество" class="fine-card">
                <div class="fine-details">
                  <h4>{{ fine.Название }}</h4>
                  <p>Стоимость: {{ fine.Стоимость }} ₽</p>
                  <p>Количество: {{ fine.Количество }}</p>
                  <p><b>Сумма: {{ fine.Сумма }} ₽</b></p>
                  <button class="btn-pay-fine" @click="payFine(fine)">Погасить штраф</button>
                </div>
              </div>
            </div>
            <div v-else class="no-fines">
              <p>У вас нет штрафов</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Profile',
  data() {
    return {
      bookings: [],
      fines: [],
      loading: true,
      loadingFines: true,
      error: null,
      finesError: null
    }
  },
  methods: {
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU')
    },
    async fetchBookings() {
      try {
        console.log('Начало запроса бронирований')
        
        // Проверяем наличие токена
        const token = localStorage.getItem('token')
        console.log('Токен авторизации:', token ? 'Присутствует' : 'Отсутствует')
        
        if (!token) {
          console.error('Токен авторизации отсутствует')
          this.error = 'Вы не авторизованы'
          this.loading = false
          return
        }
        
        console.log('Отправка запроса на /api/client/bookings')
        const response = await this.$axios.get('/api/client/bookings')
        
        console.log('Ответ от сервера получен:', response.status)
        console.log('Данные ответа:', response.data)
        
        if (response.data && Array.isArray(response.data)) {
          console.log(`Получено ${response.data.length} бронирований`)
          this.bookings = response.data
        } else {
          console.warn('Получены некорректные данные:', response.data)
          this.bookings = []
        }
      } catch (error) {
        console.error('Ошибка при загрузке бронирований:', error)
        
        if (error.response) {
          // Сервер вернул статус ошибки
          console.error('Статус ответа:', error.response.status)
          console.error('Данные ответа:', error.response.data)
          this.error = `Ошибка при загрузке: ${error.response.data.error || error.message}`
        } else if (error.request) {
          // Запрос был сделан, но ответ не получен
          console.error('Запрос отправлен, но ответ не получен')
          this.error = 'Сервер не отвечает. Попробуйте позже.'
        } else {
          // Что-то еще вызвало ошибку
          console.error('Ошибка запроса:', error.message)
          this.error = 'Ошибка при загрузке бронирований'
        }
      } finally {
        console.log('Завершение процесса загрузки бронирований')
        this.loading = false
      }
    },
    async fetchFines() {
      try {
        this.loadingFines = true
        this.finesError = null
        const response = await this.$axios.get('/api/client/fines')
        this.fines = response.data
      } catch (error) {
        console.error('Ошибка при загрузке штрафов:', error)
        this.finesError = 'Не удалось загрузить штрафы'
      } finally {
        this.loadingFines = false
      }
    },
    async payFine(fine) {
      try {
        // Для погашения нужен ID договора и ID штрафа, поэтому их нужно вернуть в API
        const response = await this.$axios.post('/api/client/pay_fine', {
          contract_id: fine.ID_договора,
          fine_id: fine.ID_штрафа
        })
        await this.fetchFines()
      } catch (error) {
        console.error('Ошибка при оплате штрафа:', error)
        this.error = 'Не удалось погасить штраф'
      }
    },
    canCancelBooking(booking) {
      const startDate = new Date(booking.Дата_начала)
      const now = new Date()
      return startDate > now && booking.Статус_договора === 'Активен'
    },
    async cancelBooking(bookingId) {
      try {
        await this.$axios.post(`/api/bookings/${bookingId}/cancel`)
        this.fetchBookings()
      } catch (error) {
        console.error('Ошибка при отмене бронирования:', error)
        this.error = 'Не удалось отменить бронирование'
      }
    },
    getCarImage(car) {
      if (!car || !car.image) return null;
      if (car.image.includes('drive.google.com/file/d/')) {
        const idMatch = car.image.match(/\/file\/d\/([^\/]+)\//)
        if (idMatch && idMatch[1]) {
          const fileId = idMatch[1]
          return `https://drive.google.com/file/d/${fileId}/preview`
        }
      }
      return car.image
    }
  },
  async mounted() {
    await this.fetchBookings()
    await this.fetchFines()
  }
}
</script>

<style scoped>
.profile-content {
  display: grid;
  gap: 2rem;
}

.booking-card, .fine-card {
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

.booking-card::before, .fine-card::before {
  content: '';
  position: absolute;
  top: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(0, 255, 157, 0.1), transparent);
  transform: translateX(-150%);
  transition: 0.5s;
}

.booking-card:hover::before, .fine-card:hover::before {
  transform: translateX(100%);
}

.booking-card:hover, .fine-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  border-color: rgba(0, 255, 157, 0.3);
}

.booking-details-flex {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.booking-details h4, .fine-details h4 {
  color: rgb(66, 185, 131);
  font-size: 1.3rem;
  margin: 0;
}

.fine-details h4 {
  color: #ff7675;
}

.booking-details p, .fine-details p {
  color: #ffffff;
  opacity: 0.8;
  margin: 0;
}

.bookings-list h3, .fines-section h3 {
  color: #ffffff;
  opacity: 0.8;
  margin-bottom: 1.5rem;
}

.fines-section {
  margin-top: 3rem;
}

.no-bookings, .no-fines {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: #ffffff;
  opacity: 0.8;
}

.fine-quantity {
  margin-left: 0.5rem;
  opacity: 0.7;
}

.btn-pay-fine {
  background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.btn-pay-fine:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 118, 117, 0.4);
}

.fines-list {
  display: grid;
  gap: 1.5rem;
}

.booking-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.car-image-container {
  width: 220px;
  height: 170px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.car-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  background: #222;
}

.car-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1rem;
  color: #ffffff;
  opacity: 0.8;
  font-weight: bold;
  font-size: 1.2rem;
}

.booking-info {
  flex-grow: 1;
  text-align: center;
}

.booking-info h4 {
  color: #42b983;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.btn-cancel {
  background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.btn-cancel:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 118, 117, 0.4);
}

.fine-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.fine-details h4 {
  color: rgb(66, 185, 131);
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.fine-details p {
  margin: 0.5rem 0;
  color: #ffffff;
  opacity: 0.8;
}
</style> 