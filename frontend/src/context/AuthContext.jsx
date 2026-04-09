import { createContext, useContext, useState } from 'react'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('trendify-user')
    return saved ? JSON.parse(saved) : null
  })

  const login = (email, password) => {
    // Mock authentication
    if (email && password.length >= 6) {
      const userData = {
        id: 1,
        name: email.split('@')[0],
        email,
      }
      setUser(userData)
      localStorage.setItem('trendify-user', JSON.stringify(userData))
      return { success: true }
    }
    return { success: false, message: 'E-posta veya şifre hatalı.' }
  }

  const register = (fullName, email, password) => {
    if (fullName && email && password.length >= 6) {
      const userData = {
        id: 1,
        name: fullName,
        email,
      }
      setUser(userData)
      localStorage.setItem('trendify-user', JSON.stringify(userData))
      return { success: true }
    }
    return { success: false, message: 'Lütfen tüm alanları doldurun.' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('trendify-user')
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
