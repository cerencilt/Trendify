import { useState, useRef, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import { recommendationAPI, analysisAPI } from '../services/api'
import {
  HiOutlinePaperAirplane,
  HiOutlineBookmark,
  HiOutlineSparkles,
} from 'react-icons/hi2'

export default function ChatPage() {
  const { darkMode } = useTheme()
  const location = useLocation()
  const analysisId = location.state?.analysisId

  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Merhaba! Analiz sonuçlarınıza göre size yardımcı olabilirim. Aşağıdaki konularda öneri alabilirsiniz:\n\n• **Paylaşım zamanı**\n• **Hashtag önerileri**\n• **Müzik önerileri**\n• **Açıklama önerileri**\n\nÖneri almak için "Öneri al" yazabilir veya sorularınızı sorabilirsiniz.',
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [savedCount, setSavedCount] = useState(0)
  const [analysisInfo, setAnalysisInfo] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Analiz bilgilerini al
  useEffect(() => {
    if (analysisId) {
      fetchAnalysisInfo()
    }
  }, [analysisId])

  const fetchAnalysisInfo = async () => {
    try {
      const response = await analysisAPI.detail(analysisId)
      setAnalysisInfo(response.data)
    } catch (err) {
      console.error('Analiz bilgisi alınamadı:', err)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isTyping) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      if (!analysisId) {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Öneri alabilmem için önce Analysis sayfasından bir analiz başlatmanız gerekiyor.',
        }])
        setIsTyping(false)
        return
      }

      // Backend'den AI önerisi al
      const response = await recommendationAPI.generate({
        analysis_id: analysisId,
        platform: analysisInfo?.platform,
        topic: analysisInfo?.topic,
      })

      const recommendation = response.data

      // AI cevabını formatla
      let aiContent = recommendation.reasoning || ''

      if (recommendation.post_time !== null) {
        aiContent += `\n\n📅 **En iyi paylaşım zamanı:** ${recommendation.best_day} ${recommendation.post_time}:00`
      }

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiContent,
        recommendationId: recommendation.id,
      }])

    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Bir hata oluştu. Lütfen tekrar deneyin.'
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ ${errorMsg}`,
      }])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSaveRecommendation = () => {
    setSavedCount(prev => prev + 1)
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* Context Panel */}
      <div className={`w-72 flex-shrink-0 rounded-2xl p-5 overflow-y-auto
        ${darkMode
          ? 'bg-dark-800/80 border border-dark-700/50'
          : 'bg-white border border-gray-200 shadow-sm'
        }`}
      >
        <h3 className={`font-display font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          Context
        </h3>

        <div className="space-y-4">
          <div>
            <p className={`text-xs font-medium uppercase tracking-wider mb-1 ${darkMode ? 'text-dark-500' : 'text-gray-400'}`}>
              Last Analysis
            </p>
            <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {analysisInfo
                ? `${analysisInfo.topic} on ${analysisInfo.platform}`
                : 'Analiz seçilmedi'}
            </p>
          </div>

          {analysisInfo?.result && (
            <div>
              <p className={`text-xs font-medium uppercase tracking-wider mb-2 ${darkMode ? 'text-dark-500' : 'text-gray-400'}`}>
                Analysis Stats
              </p>
              <div className={`text-sm space-y-1 ${darkMode ? 'text-dark-200' : 'text-gray-700'}`}>
                <p>📊 Engagement: %{analysisInfo.result.avg_engagement_rate?.toFixed(1)}</p>
                <p>🎯 Trend Score: {Math.round(analysisInfo.result.trend_fit_score)}/100</p>
              </div>
            </div>
          )}

          {savedCount > 0 && (
            <div className={`p-3 rounded-xl ${darkMode ? 'bg-green-500/10 border border-green-500/20' : 'bg-green-50 border border-green-200'}`}>
              <p className={`text-xs ${darkMode ? 'text-green-400' : 'text-green-700'}`}>
                {savedCount} öneri kaydedildi
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className={`flex-1 rounded-2xl p-5 overflow-y-auto mb-4
          ${darkMode
            ? 'bg-dark-800/80 border border-dark-700/50'
            : 'bg-white border border-gray-200 shadow-sm'
          }`}
        >
          <div className="space-y-4">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                    ${msg.role === 'user'
                      ? 'bg-primary-600 text-white rounded-br-md'
                      : darkMode
                        ? 'bg-dark-700/80 text-dark-100 rounded-bl-md border border-dark-600/30'
                        : 'bg-gray-100 text-gray-800 rounded-bl-md'
                    }`}
                >
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-1.5 mb-2">
                      <HiOutlineSparkles className="w-4 h-4 text-primary-400" />
                      <span className={`text-xs font-medium ${darkMode ? 'text-primary-400' : 'text-primary-600'}`}>
                        Trendify AI
                      </span>
                    </div>
                  )}
                  {msg.content.split('**').map((part, i) =>
                    i % 2 === 0 ? part : <strong key={i}>{part}</strong>
                  )}
                </div>
              </motion.div>
            ))}

            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className={`px-4 py-3 rounded-2xl rounded-bl-md ${darkMode ? 'bg-dark-700/80 border border-dark-600/30' : 'bg-gray-100'}`}>
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className={`rounded-2xl p-3 flex items-center gap-3
          ${darkMode
            ? 'bg-dark-800/80 border border-dark-700/50'
            : 'bg-white border border-gray-200 shadow-sm'
          }`}
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask for captions, hashtags, or reasoning..."
            className={`flex-1 bg-transparent border-none outline-none text-sm px-2
              ${darkMode ? 'text-white placeholder-dark-400' : 'text-gray-900 placeholder-gray-400'}`}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="p-2.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white transition-all
                       disabled:opacity-40 disabled:hover:bg-primary-600"
          >
            <HiOutlinePaperAirplane className="w-4 h-4" />
          </button>
        </div>

        {/* Save Recommendation */}
        <button
          onClick={handleSaveRecommendation}
          className={`mt-3 w-full py-3 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2
            ${darkMode
              ? 'bg-dark-800 border border-dark-700/50 text-dark-300 hover:text-white hover:border-primary-500/30'
              : 'bg-white border border-gray-200 text-gray-600 hover:text-gray-900 hover:border-primary-300 shadow-sm'
            }`}
        >
          <HiOutlineBookmark className="w-4 h-4" />
          Save Recommendation
        </button>
      </div>
    </div>
  )
}