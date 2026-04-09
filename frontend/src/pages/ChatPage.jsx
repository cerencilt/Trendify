import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import { mockChatMessages, mockTrendingHashtags } from '../data/mockData'
import {
  HiOutlinePaperAirplane,
  HiOutlineBookmark,
  HiOutlineSparkles,
} from 'react-icons/hi2'

// Simulated AI responses
const aiResponses = {
  zaman: 'Analiz verilerine göre, bu tür içerikler **Salı ve Cuma günleri 19:00-21:00** arasında en yüksek etkileşimi almaktadır. Benzer profildeki içerik üreticiler bu saat diliminde %25 daha fazla beğeni almıştır.',
  hashtag: 'İçeriğiniz için şu hashtag\'leri öneriyorum:\n\n• #fashiontrends\n• #sustainablestyle\n• #outfitinspo\n• #modatrend\n• #styleoftheday\n\nBu etiketler son 7 günde keşfet sayfasında %18 daha fazla görünürlük sağlamıştır.',
  muzik: 'Şu an trend olan ve içeriğinize uygun sesler:\n\n🎵 "Espresso" - Sabrina Carpenter\n🎵 "Birds of a Feather" - Billie Eilish\n🎵 "Nasty" - Tinashe\n\nBu sesler Instagram Reels\'de son hafta en çok kullanılan 10 ses arasında yer almaktadır.',
  aciklama: 'İçeriğiniz için önerilen açıklama:\n\n"Stilini keşfet, trendleri yakala ✨ Bu sezon en çok tercih edilen parçalar burada! Hangisi senin favorin? 👇"\n\nSoru sorarak biten açıklamalar yorum oranını %40 artırmaktadır.',
  default: 'Analiz sonuçlarınıza göre size yardımcı olabilirim. Aşağıdaki konularda öneri alabilisiniz:\n\n• **Paylaşım zamanı** - En uygun gün ve saat önerileri\n• **Hashtag önerileri** - Trend etiketler\n• **Müzik önerileri** - Popüler sesler\n• **Açıklama önerileri** - Etkileşimi artıran metinler',
}

function getAIResponse(message) {
  const lower = message.toLowerCase()
  if (lower.includes('zaman') || lower.includes('saat') || lower.includes('gün') || lower.includes('ne zaman')) {
    return aiResponses.zaman
  }
  if (lower.includes('hashtag') || lower.includes('etiket') || lower.includes('tag')) {
    return aiResponses.hashtag
  }
  if (lower.includes('müzik') || lower.includes('ses') || lower.includes('şarkı') || lower.includes('music')) {
    return aiResponses.muzik
  }
  if (lower.includes('açıklama') || lower.includes('caption') || lower.includes('metin') || lower.includes('description')) {
    return aiResponses.aciklama
  }
  return aiResponses.default
}

export default function ChatPage() {
  const { darkMode } = useTheme()
  const [messages, setMessages] = useState(mockChatMessages)
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [savedCount, setSavedCount] = useState(0)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!input.trim() || isTyping) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI thinking
    setTimeout(() => {
      const response = getAIResponse(userMessage.content)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: response,
      }])
      setIsTyping(false)
    }, 1000 + Math.random() * 1000)
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
              Moda on Instagram (Engagement)
            </p>
          </div>

          <div>
            <p className={`text-xs font-medium uppercase tracking-wider mb-2 ${darkMode ? 'text-dark-500' : 'text-gray-400'}`}>
              Trending Now
            </p>
            <div className="flex flex-wrap gap-1.5">
              {mockTrendingHashtags.slice(0, 6).map(tag => (
                <span
                  key={tag}
                  className={`text-xs px-2 py-1 rounded-md
                    ${darkMode
                      ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                      : 'bg-primary-50 text-primary-600 border border-primary-200'
                    }`}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

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
