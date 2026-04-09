import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineChartBar, HiOutlineCpuChip, HiOutlineSparkles } from 'react-icons/hi2'

const features = [
  {
    icon: HiOutlineChartBar,
    title: 'Analyze',
    description: 'Real-time data insights',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: HiOutlineCpuChip,
    title: 'Predict',
    description: 'AI-powered trend forecasting',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: HiOutlineSparkles,
    title: 'Create',
    description: 'Content that goes viral',
    color: 'from-orange-500 to-red-500',
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark-950 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary-500/5 rounded-full blur-3xl" />
      </div>

      {/* Grid overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), 
                           linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
        }}
      />

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h1 className="font-display text-7xl font-bold mb-4">
            <span className="gradient-text">Trendify</span>
          </h1>
          <p className="text-dark-300 text-xl font-light tracking-wide">
            Next-Gen AI Trend Analysis for Creators
          </p>
        </motion.div>

        {/* Feature cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex gap-6 mb-16"
        >
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 + i * 0.1 }}
              className="group relative"
            >
              <div className="w-48 p-6 rounded-2xl border border-dark-700/50 bg-dark-800/60 backdrop-blur-sm
                            hover:border-primary-500/30 transition-all duration-300 text-center cursor-default">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} 
                              flex items-center justify-center mx-auto mb-4 
                              group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-display text-lg font-semibold text-white mb-1">
                  {feature.title}
                </h3>
                <p className="text-dark-400 text-sm">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Link
            to="/login"
            className="group relative inline-flex items-center gap-2 px-10 py-4 
                       bg-primary-600 hover:bg-primary-500 text-white font-display font-semibold 
                       text-lg rounded-2xl transition-all duration-300 
                       shadow-2xl shadow-primary-600/30 hover:shadow-primary-500/40
                       hover:-translate-y-0.5"
          >
            TRY TRENDIFY
            <span className="group-hover:translate-x-1 transition-transform duration-200">→</span>
          </Link>
        </motion.div>

        {/* Bottom decoration */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="absolute bottom-8 text-dark-500 text-sm"
        >
          Beykent Üniversitesi — Yazılım Mühendisliği Bitirme Projesi 2026
        </motion.p>
      </div>
    </div>
  )
}
