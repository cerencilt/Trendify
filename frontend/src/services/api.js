import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_URL,
})

// Her istekte token ekle (eğer varsa) ve Content-Type ayarla
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('trendify-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // FormData ise Content-Type'ı browser otomatik ayarlasın
  // (multipart/form-data; boundary=... şeklinde gerekli)
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json'
  }

  return config
})

// Token süresi dolduğunda otomatik refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token süresi dolmuş, logout yap
      localStorage.removeItem('trendify-token')
      localStorage.removeItem('trendify-refresh-token')
      localStorage.removeItem('trendify-user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============ AUTH ============
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login/', { email, password }),

  register: (username, email, password) =>
    api.post('/auth/register/', { username, email, password }),

  me: () => api.get('/auth/me/'),
}

// ============ ANALYSIS ============
export const analysisAPI = {
  start: (data) => api.post('/analysis/start/', data),
  list: () => api.get('/analysis/'),
  detail: (id) => api.get(`/analysis/${id}/`),
  result: (id) => api.get(`/analysis/${id}/result/`),
}

// ============ RECOMMENDATIONS ============
export const recommendationAPI = {
  generate: (data) => api.post('/recommendations/generate/', data),
  list: () => api.get('/recommendations/'),
  detail: (id) => api.get(`/recommendations/${id}/`),
  feedback: (id, data) => api.post(`/recommendations/${id}/feedback/`, data),
}

// ============ DASHBOARD ============
export const dashboardAPI = {
  summary: () => api.get('/dashboard/summary/'),
  history: (filters = {}) => api.get('/dashboard/history/', { params: filters }),
}

export default api