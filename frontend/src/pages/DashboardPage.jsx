import { useState } from 'react'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import { mockAnalyses } from '../data/mockData'
import {
  HiOutlineMagnifyingGlass,
  HiOutlineFunnel,
  HiOutlineStar,
  HiOutlineEye,
} from 'react-icons/hi2'

export default function DashboardPage() {
  const { darkMode } = useTheme()

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [platformFilter, setPlatformFilter] = useState('All Platforms')
  const [sortOrder, setSortOrder] = useState('Newest First')

  // Feedback
  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackSent, setFeedbackSent] = useState(false)

  // Detail modal
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)

  // Filter & sort logic
  const filtered = mockAnalyses
    .filter(a => {
      if (platformFilter !== 'All Platforms' && a.platform !== platformFilter) return false
      if (searchTerm && !a.topic.toLowerCase().includes(searchTerm.toLowerCase())) return false
      return true
    })
    .sort((a, b) => {
      if (sortOrder === 'Newest First') return new Date(b.date) - new Date(a.date)
      if (sortOrder === 'Oldest First') return new Date(a.date) - new Date(b.date)
      if (sortOrder === 'Highest Engagement') return b.predictedEngagement - a.predictedEngagement
      return 0
    })

  const handleFeedbackSubmit = () => {
    if (rating === 0) return
    setFeedbackSent(true)
    setTimeout(() => setFeedbackSent(false), 3000)
    setRating(0)
    setFeedbackText('')
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className={`font-display text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Dashboard
          </h1>
          <p className={`mt-1 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>
            Analiz geçmişiniz ve performans özetleriniz
          </p>
        </div>
        <span className="font-display text-lg font-semibold gradient-text">Trendify</span>
      </div>

      {/* Filters */}
      <div className={`rounded-2xl p-4 mb-6 flex items-center gap-4
        ${darkMode ? 'bg-dark-800/80 border border-dark-700/50' : 'bg-white border border-gray-200 shadow-sm'}`}
      >
        {/* Search */}
        <div className="flex-1 relative">
          <HiOutlineMagnifyingGlass className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${darkMode ? 'text-dark-400' : 'text-gray-400'}`} />
          <input
            type="text"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Search topics..."
            className={`w-full pl-10 pr-4 py-2.5 rounded-xl text-sm
              ${darkMode
                ? 'bg-dark-700/50 border border-dark-600 text-white placeholder-dark-400 focus:border-primary-500'
                : 'bg-gray-50 border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-primary-500'
              } outline-none transition-colors`}
          />
        </div>

        {/* Platform filter */}
        <select
          value={platformFilter}
          onChange={e => setPlatformFilter(e.target.value)}
          className={`px-4 py-2.5 rounded-xl text-sm
            ${darkMode
              ? 'bg-dark-700/50 border border-dark-600 text-white'
              : 'bg-gray-50 border border-gray-200 text-gray-900'
            } outline-none`}
        >
          <option>All Platforms</option>
          <option>Instagram</option>
          <option>TikTok</option>
          <option>YouTube</option>
        </select>

        {/* Sort */}
        <select
          value={sortOrder}
          onChange={e => setSortOrder(e.target.value)}
          className={`px-4 py-2.5 rounded-xl text-sm
            ${darkMode
              ? 'bg-dark-700/50 border border-dark-600 text-white'
              : 'bg-gray-50 border border-gray-200 text-gray-900'
            } outline-none`}
        >
          <option>Newest First</option>
          <option>Oldest First</option>
          <option>Highest Engagement</option>
        </select>
      </div>

      {/* Analysis Table */}
      <div className={`rounded-2xl overflow-hidden mb-8
        ${darkMode ? 'bg-dark-800/80 border border-dark-700/50' : 'bg-white border border-gray-200 shadow-sm'}`}
      >
        <table className="w-full">
          <thead>
            <tr className={darkMode ? 'bg-dark-700/50' : 'bg-gray-50'}>
              {['Date', 'Platform', 'Topic', 'Pred. Eng.', 'Best Time', 'Actions'].map(header => (
                <th
                  key={header}
                  className={`px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider
                    ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className={`divide-y ${darkMode ? 'divide-dark-700/30' : 'divide-gray-100'}`}>
            {filtered.length > 0 ? (
              filtered.map((analysis, i) => (
                <motion.tr
                  key={analysis.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`${darkMode ? 'hover:bg-dark-700/30' : 'hover:bg-gray-50'} transition-colors`}
                >
                  <td className={`px-6 py-4 text-sm ${darkMode ? 'text-dark-200' : 'text-gray-700'}`}>
                    {analysis.date}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-lg
                      ${analysis.platform === 'Instagram'
                        ? 'bg-pink-500/10 text-pink-400 border border-pink-500/20'
                        : analysis.platform === 'TikTok'
                          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                          : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}
                    >
                      {analysis.platform}
                    </span>
                  </td>
                  <td className={`px-6 py-4 text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {analysis.topic}
                  </td>
                  <td className={`px-6 py-4 text-sm font-mono ${darkMode ? 'text-dark-200' : 'text-gray-700'}`}>
                    {analysis.predictedEngagement.toFixed(3)}
                  </td>
                  <td className={`px-6 py-4 text-sm ${darkMode ? 'text-dark-200' : 'text-gray-700'}`}>
                    {analysis.bestTime}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => setSelectedAnalysis(analysis)}
                      className={`text-xs font-medium px-3 py-1.5 rounded-lg transition-colors
                        ${darkMode
                          ? 'text-primary-400 hover:bg-primary-500/10'
                          : 'text-primary-600 hover:bg-primary-50'
                        }`}
                    >
                      Detail
                    </button>
                  </td>
                </motion.tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center">
                  <p className={`text-sm ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>
                    Henüz analiz bulunmuyor. Yeni bir analiz başlatın.
                  </p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedAnalysis && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={() => setSelectedAnalysis(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={e => e.stopPropagation()}
            className={`w-full max-w-lg mx-4 rounded-2xl p-6 shadow-2xl
              ${darkMode ? 'bg-dark-800 border border-dark-700' : 'bg-white border border-gray-200'}`}
          >
            <h3 className={`font-display text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {selectedAnalysis.topic}
            </h3>
            <div className="grid grid-cols-2 gap-4 mb-6">
              {[
                { label: 'Platform', value: selectedAnalysis.platform },
                { label: 'Tarih', value: selectedAnalysis.date },
                { label: 'Tahmini Etkileşim', value: `${selectedAnalysis.predictedEngagement.toFixed(3)}%` },
                { label: 'En İyi Zaman', value: selectedAnalysis.bestTime },
                { label: 'Trend Fit Score', value: `${selectedAnalysis.trendFitScore}/100` },
                { label: 'Analiz Tipi', value: selectedAnalysis.type === 'content' ? 'İçerik Bazlı' : 'Performans Bazlı' },
              ].map(item => (
                <div key={item.label}>
                  <p className={`text-xs ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>{item.label}</p>
                  <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>{item.value}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => setSelectedAnalysis(null)}
              className="btn-primary w-full"
            >
              Kapat
            </button>
          </motion.div>
        </motion.div>
      )}

      {/* Feedback Section */}
      <div className={`rounded-2xl p-6
        ${darkMode ? 'bg-dark-800/80 border border-dark-700/50' : 'bg-white border border-gray-200 shadow-sm'}`}
      >
        <h3 className={`font-display text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          Feedback
        </h3>

        {/* Star Rating */}
        <div className="flex items-center gap-1 mb-4">
          <span className={`text-sm mr-2 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>Rate us:</span>
          {[1, 2, 3, 4, 5].map(star => (
            <button
              key={star}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
              className="transition-transform hover:scale-110"
            >
              <HiOutlineStar
                className={`w-6 h-6 transition-colors ${
                  star <= (hoverRating || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : darkMode ? 'text-dark-500' : 'text-gray-300'
                }`}
              />
            </button>
          ))}
        </div>

        {/* Feedback text */}
        <input
          type="text"
          value={feedbackText}
          onChange={e => setFeedbackText(e.target.value)}
          placeholder="Any suggestions?"
          className={`w-full mb-4 ${darkMode ? 'input-field' : 'input-field-light'}`}
        />

        <button onClick={handleFeedbackSubmit} disabled={rating === 0} className="btn-primary disabled:opacity-50">
          Submit Feedback
        </button>

        {feedbackSent && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-3 text-sm text-green-400"
          >
            Geri bildiriminiz kaydedildi. Teşekkürler!
          </motion.p>
        )}
      </div>
    </div>
  )
}
