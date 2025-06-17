export default {
  namespaced: true,
  
  state: {
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  },
  
  mutations: {
    setToken(state, token) {
      state.token = token
      state.isAuthenticated = true
      localStorage.setItem('token', token)
    },
    clearToken(state) {
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    }
  },
  
  actions: {
    logout({ commit }) {
      commit('clearToken')
    }
  }
} 