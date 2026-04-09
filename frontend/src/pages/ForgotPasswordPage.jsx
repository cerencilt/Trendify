import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    if (!email.trim()) {
      setError('E-posta alanı zorunludur.')
      return
    }
    setSent(true)
  }

  return (
    <div className="min-h-screen bg-dark-950 relative overflow-hidden flex items-center justify-center">
      <div className="absolute inset-0">
        <div className="absolute top-1/3 right-1/4 w-[500px] h-[500px] bg-primary-600/8 rounded-full blur-3xl" />
      </div>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }} className="relative z-10 w-full max-w-md mx-4">
        <div className="rounded-3xl border border-dark-700/50 bg-dark-800/80 backdrop-blur-xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <Link to="/" className="inline-block mb-6">
              <h1 className="font-display text-3xl font-bold gradient-text">Trendify</h1>
            </Link>
            <h2 className="font-display text-2xl font-semibold text-white mb-2">Şifre Sıfırlama</h2>
            <p className="text-dark-400 text-sm">E-posta adresinize sıfırlama bağlantısı göndereceğiz.</p>
          </div>
          {sent ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </div>
              <p className="text-white font-medium mb-2">Bağlantı gönderildi!</p>
              <p className="text-dark-400 text-sm mb-6">{email} adresine şifre sıfırlama bağlantısı gönderdik.</p>
              <Link to="/login" className="btn-primary inline-block">Giriş Sayfasına Dön</Link>
            </motion.div>
          ) : (
            <>
              {error && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</motion.div>
              )}
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">Email</label>
                  <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="name@example.com" className="input-field" />
                </div>
                <button type="submit" className="btn-primary w-full">Sıfırlama Bağlantısı Gönder</button>
              </form>
              <div className="mt-6 text-center text-sm">
                <Link to="/login" className="text-primary-400 hover:text-primary-300 transition-colors">← Giriş sayfasına dön</Link>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
}