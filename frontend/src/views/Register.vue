<template>
  <div class="page-container">
    <h1 class="page-title">Регистрация</h1>
    <div class="content-section">
      <form @submit.prevent="register" class="register-form">
        <!-- Основные данные -->
        <div class="form-section">
          <h3>Личные данные</h3>
          <div class="form-group">
            <label class="form-label">Фамилия</label>
            <input v-model="form.surname" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Имя и Отчество</label>
            <input v-model="form.name" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Пол</label>
            <select v-model="form.gender" class="form-input" required>
              <option value="М">Мужской</option>
              <option value="Ж">Женский</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Дата рождения</label>
            <input v-model="form.birthdate" type="date" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Пароль</label>
            <input v-model="form.password" type="password" class="form-input" required>
          </div>
        </div>

        <!-- Телефон -->
        <div class="form-section">
          <h3>Контактный телефон</h3>
          <div class="form-group">
            <label class="form-label">Номер телефона</label>
            <input v-model="form.phone.number" type="tel" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Тип телефона</label>
            <select v-model="form.phone.type" class="form-input">
              <option value="Мобильный">Мобильный</option>
              <option value="Домашний">Домашний</option>
            </select>
          </div>
        </div>

        <!-- Паспорт -->
        <div class="form-section">
          <h3>Паспортные данные</h3>
          <div class="form-group">
            <label class="form-label">Серия и номер</label>
            <input v-model="form.passport.series_number" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Дата выдачи</label>
            <input v-model="form.passport.issue_date" type="date" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Срок действия</label>
            <input v-model="form.passport.expiry_date" type="date" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Кем выдан</label>
            <input v-model="form.passport.issued_by" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Код подразделения</label>
            <input v-model="form.passport.department_code" type="text" class="form-input" required>
          </div>
        </div>

        <!-- Водительское удостоверение -->
        <div class="form-section">
          <h3>Водительское удостоверение</h3>
          <div class="form-group">
            <label class="form-label">Номер</label>
            <input v-model="form.license.number" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Дата выдачи</label>
            <input v-model="form.license.issue_date" type="date" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Срок действия</label>
            <input v-model="form.license.expiry_date" type="date" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Место выдачи</label>
            <input v-model="form.license.issue_place" type="text" class="form-input" required>
          </div>
        </div>

        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" class="btn" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      form: {
        surname: '',
        name: '',
        gender: 'М',
        birthdate: '',
        email: '',
        password: '',
        phone: {
          number: '',
          type: 'Мобильный'
        },
        passport: {
          series_number: '',
          issue_date: '',
          expiry_date: '',
          issued_by: '',
          department_code: ''
        },
        license: {
          number: '',
          issue_date: '',
          expiry_date: '',
          issue_place: ''
        }
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async register() {
      this.loading = true
      this.error = null
      try {
        const response = await this.$axios.post('/api/register', this.form)
        if (response.status === 201) {
          this.$router.push('/login')
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Ошибка при регистрации'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-section h3 {
  color: rgb(66, 185, 131);
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
}

@media (max-width: 768px) {
  .form-section {
    padding: 1.5rem;
  }
}
</style> 