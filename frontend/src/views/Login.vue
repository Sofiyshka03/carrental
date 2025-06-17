<template>
  <div class="page-container">
    <h1 class="page-title">Вход в систему</h1>
    <div class="content-section">
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input 
            v-model="email" 
            type="email" 
            class="form-input"
            required
          >
        </div>
        <div class="form-group">
          <label class="form-label">Пароль</label>
          <input 
            v-model="password" 
            type="password" 
            class="form-input"
            required
          >
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" class="btn" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        <div class="register-link">
          <router-link to="/register">Нет аккаунта? Зарегистрируйтесь</router-link>
        </div>
        <div class="employee-login-link">
          <router-link to="/employee-login">Вход для сотрудников</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: null,
      loading: false
    }
  },
  methods: {
    async login() {
      try {
        this.loading = true
        const response = await this.$axios.post('/api/login', { email: this.email, password: this.password })
        const token = response.data.token
        this.$store.commit('auth/setToken', token)
        this.$router.push('/')
      } catch (error) {
        this.error = error.response?.data?.error || 'Ошибка при входе'
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

/* Делаем контейнер уже */
.content-section {
  max-width: 500px;
  margin: 0 auto;
}

.register-link, .employee-login-link {
  margin-top: 1.5rem;
  text-align: center;
}

.register-link a, .employee-login-link a {
  color: rgb(66, 185, 131);
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.register-link a:hover, .employee-login-link a:hover {
  opacity: 1;
}

.employee-login-link {
  margin-top: 0.8rem;
  font-size: 0.9rem;
}

.employee-login-link a {
  color: #b3b3b3;
}
</style> 