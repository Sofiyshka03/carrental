<template>
  <div class="page-container">
    <h1 class="page-title">Вход для сотрудников</h1>
    <div class="content-section">
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input 
            type="email" 
            v-model="email" 
            class="form-input"
            required 
            placeholder="Введите email"
          >
        </div>
        
        <div class="form-group">
          <label class="form-label">Пароль</label>
          <input 
            type="password" 
            v-model="password" 
            class="form-input"
            required 
            placeholder="Введите пароль"
          >
        </div>
        
        <div v-if="errorMessage" class="error">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="btn" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        
        <div class="login-links">
          <router-link to="/">Вернуться на главную</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmployeeLogin',
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await axios.post('/api/employee/login', {
          email: this.email,
          password: this.password
        })
        
        // Сохраняем токен и информацию о сотруднике
        localStorage.setItem('employee_token', response.data.token)
        localStorage.setItem('employee_info', JSON.stringify(response.data.employee))
        
        // Устанавливаем токен для всех будущих запросов
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
        
        // Перенаправляем в личный кабинет сотрудника
        this.$router.push('/employee-cabinet')
      } catch (error) {
        console.error('Ошибка при входе:', error)
        if (error.response && error.response.data && error.response.data.error) {
          this.errorMessage = error.response.data.error
        } else {
          this.errorMessage = 'Ошибка при входе. Пожалуйста, попробуйте снова.'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
}

.content-section {
  max-width: 500px;
  margin: 0 auto;
}

.login-links {
  margin-top: 1.5rem;
  text-align: center;
}

.login-links a {
  color: rgb(66, 185, 131);
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.login-links a:hover {
  opacity: 1;
}
</style> 