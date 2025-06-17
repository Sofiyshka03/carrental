import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

const app = createApp(App)

// Настройка базового URL для axios
axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000'

// Добавляем перехватчик для автоматической установки токена авторизации
axios.interceptors.request.use(config => {
  // Проверяем наличие токена сотрудника
  const employeeToken = localStorage.getItem('employee_token')
  if (employeeToken) {
    config.headers['Authorization'] = `Bearer ${employeeToken}`
  } else {
    // Если нет токена сотрудника, проверяем клиентский токен
    const clientToken = localStorage.getItem('token')
    if (clientToken) {
      config.headers['Authorization'] = `Bearer ${clientToken}`
    }
  }
  return config
})

// Перехватчик ответов для обработки ошибок авторизации
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Если сервер вернул 401 (Unauthorized), очищаем токены и перенаправляем на страницу входа
      localStorage.removeItem('employee_token')
      localStorage.removeItem('employee_info')
      localStorage.removeItem('token')
      localStorage.removeItem('user_info')
      
      // Если текущий маршрут требует авторизации сотрудника, перенаправляем на вход для сотрудников
      if (router.currentRoute.value.meta.requiresEmployeeAuth) {
        router.push('/employee-login')
      }
    }
    return Promise.reject(error)
  }
)

app.config.globalProperties.$axios = axios

app.use(router)
app.use(store)
app.mount('#app') 