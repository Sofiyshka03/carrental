import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CarList from '../views/CarList.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import Booking from '../views/Booking.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/cars',
    name: 'Cars',
    component: CarList
  },
  {
    path: '/booking/:id',
    name: 'Booking',
    component: Booking
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/employee-cabinet',
    name: 'EmployeeCabinet',
    component: () => import('../views/EmployeeCabinet.vue'),
    meta: { requiresEmployeeAuth: true }
  },
  {
    path: '/employee-login',
    name: 'EmployeeLogin',
    component: () => import('../views/EmployeeLogin.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.state.auth.isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  } else if (to.matched.some(record => record.meta.requiresEmployeeAuth)) {
    const token = localStorage.getItem('employee_token')
    if (!token) {
      next({ path: '/employee-login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 