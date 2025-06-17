<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="brand">CarRental</router-link>
      <div class="nav-links">
        <router-link to="/cars">Автомобили</router-link>
        <template v-if="isAuthenticated">
          <router-link to="/profile">Личный кабинет</router-link>
          <a @click="logout" class="logout-link">Выйти</a>
        </template>
        <template v-else-if="isEmployeeLoggedIn">
          <router-link to="/employee-cabinet">Кабинет сотрудника</router-link>
          <a @click="employeeLogout" class="logout-link">Выйти</a>
        </template>
        <template v-else>
          <div class="login-dropdown">
            <router-link to="/login">Войти</router-link>
            <div class="dropdown-content">
              <router-link to="/employee-login">Вход для сотрудников</router-link>
            </div>
          </div>
          <router-link to="/register">Регистрация</router-link>
        </template>
      </div>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isAuthenticated() {
      return this.$store.state.auth.isAuthenticated
    }
  },
  data() {
    return {
      isEmployeeLoggedIn: false
    }
  },
  created() {
    this.checkEmployeeAuth()
    
    this.$router.beforeEach((to, from, next) => {
      this.checkEmployeeAuth()
      next()
    })
  },
  methods: {
    logout() {
      this.$store.dispatch('auth/logout')
      this.$router.push('/login')
    },
    employeeLogout() {
      localStorage.removeItem('employee_token')
      localStorage.removeItem('employee_info')
      this.isEmployeeLoggedIn = false
      this.$router.push('/employee-login')
    },
    checkEmployeeAuth() {
      const token = localStorage.getItem('employee_token')
      this.isEmployeeLoggedIn = !!token
    }
  }
}
</script>

<style>
/* Общие стили для всего приложения */
body {
  margin: 0;
  padding: 0;
  background-color: #1a1a1a;
  color: #ffffff;
}

/* Общий контейнер для всех страниц */
.page-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 64px);
}

/* Общие стили для заголовков */
.page-title {
  color: rgb(66, 185, 131);
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

/* Общие стили для секций */
.content-section {
  background: #2a2a2a;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Общие стили для карточек */
.card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 255, 157, 0.3);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

/* Общие стили для кнопок */
.btn {
  background: linear-gradient(135deg, #0066ff 0%, rgb(66, 185, 131) 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  text-decoration: none;
  display: inline-block;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
}

.btn:disabled {
  background: #4a4a4a;
  cursor: not-allowed;
  transform: none;
}

/* Общие стили для текста */
.text-content {
  color: #ffffff;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1.1rem;
}

/* Общие стили для состояний загрузки и ошибок */
.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #ff4444;
}

/* Общие стили для форм */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: rgb(66, 185, 131);
  font-size: 1.1rem;
}

.form-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
}

select.form-input {
  background-color: rgba(42, 42, 42, 0.9);
  color: white;
  appearance: none;
  padding-right: 2rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2342b983' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.7rem center;
  background-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: rgb(66, 185, 131);
}

/* Выпадающее меню для входа */
.login-dropdown {
  position: relative;
  display: inline-block;
}

.login-dropdown .dropdown-content {
  display: none;
  position: absolute;
  background-color: #2a2a2a;
  min-width: 200px;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  z-index: 1;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
}

.login-dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-content a {
  display: block;
  padding: 12px 16px;
  text-align: center;
  border-radius: 4px;
}

.dropdown-content a:hover {
  background-color: rgba(66, 185, 131, 0.1);
}

/* Адаптивность */
@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
  
  .content-section {
    padding: 1.5rem;
  }
}

.navbar {
  background: rgba(26, 26, 26, 0.95);
  border-radius: 0;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: rgb(66, 185, 131);
}

.nav-links {
  display: flex;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
  align-items: center;
}

.nav-links a {
  color: #ffffff;
  opacity: 0.8;
  text-decoration: none;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-links a:hover,
.nav-links a.active {
  color: rgb(66, 185, 131);
  background: rgba(0, 255, 157, 0.1);
}


.logout-link {
  cursor: pointer;
  color: #ffffff;
  opacity: 0.8;
  font-weight: 500;
}

.logout-link:hover {
  color: rgb(66, 185, 131);
}

.router-link-active {
  color: rgb(66, 185, 131);
}
</style> 