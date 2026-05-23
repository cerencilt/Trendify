import { createContext, useContext, useState } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('trendify-user')
    return saved ? JSON.parse(saved) : null
  })

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password)
      const { access, refresh } = response.data

      // Token'ları sakla
      localStorage.setItem('trendify-token', access)
      localStorage.setItem('trendify-refresh-token', refresh)

      // Kullanıcı bilgilerini al
      const meResponse = await authAPI.me()
      const userData = meResponse.data

      setUser(userData)
      localStorage.setItem('trendify-user', JSON.stringify(userData))

      return { success: true }
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'E-posta veya şifre hatalı.'
      return { success: false, message }
    }
  }

  const register = async (fullName, email, password) => {
    try {
      // Username olarak email'in @ öncesini kullan
      const username = email.split('@')[0]

      await authAPI.register(username, email, password)

      // Kayıt başarılıysa otomatik login
      return await login(email, password)
    } catch (error) {
      const message =
        error.response?.data?.email?.[0] ||
        error.response?.data?.username?.[0] ||
        error.response?.data?.password?.[0] ||
        'Kayıt sırasında bir hata oluştu.'
      return { success: false, message }
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('trendify-user')
    localStorage.removeItem('trendify-token')
    localStorage.removeItem('trendify-refresh-token')
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)