import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!email.trim()) {
      setError('E-posta alanı zorunludur.')
      return
    }
    if (!password.trim()) {
      setError('Şifre alanı zorunludur.')
      return
    }
    if (password.length < 6) {
      setError('Şifre en az 6 karakter olmalıdır.')
      return
    }

    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      const result = login(email, password)
      if (result.success) {
        navigate('/app/analysis')
      } else {
        setError(result.message)
      }
      setLoading(false)
    }, 600)
  }

  return (
    <div className="min-h-screen bg-dark-950 relative overflow-hidden flex items-center justify-center">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary-600/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-600/8 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md mx-4"
      >
        <div className="rounded-3xl border border-dark-700/50 bg-dark-800/80 backdrop-blur-xl p-8 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <Link to="/" className="inline-block mb-6">
              <h1 className="font-display text-3xl font-bold gradient-text">Trendify</h1>
            </Link>
            <h2 className="font-display text-2xl font-semibold text-white mb-2">
              Welcome to Trendify
            </h2>
            <p className="text-dark-400">
              Log in to start analyzing trends
            </p>
          </div>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Footer links */}
          <div className="mt-6 text-center text-sm">
            <button className="text-primary-400 hover:text-primary-300 transition-colors">
              Forgot Password?
            </button>
            <span className="text-dark-500 mx-2">•</span>
            <Link to="/register" className="text-primary-400 hover:text-primary-300 transition-colors font-medium">
              Sign Up
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
