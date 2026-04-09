import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import { platforms, goals, languages } from '../data/mockData'
import {
  HiOutlineDocumentText,
  HiOutlineChartBarSquare,
  HiOutlineArrowUpTray,
  HiOutlineSparkles,
  HiOutlineCheck,
  HiOutlineClock,
  HiOutlineFire,
  HiOutlineArrowRight,
} from 'react-icons/hi2'

export default function AnalysisPage() {
  const { darkMode } = useTheme()
  const navigate = useNavigate()

  // Tabs
  const [activeTab, setActiveTab] = useState('content') // content | performance

  // Step management
  const [step, setStep] = useState(1) // 1: Data Entry, 2: Results, 3: Recommendations

  // Content-based form
  const [topic, setTopic] = useState('')
  const [platform, setPlatform] = useState('Instagram')
  const [goal, setGoal] = useState(goals[0])
  const [language, setLanguage] = useState(languages[0])
  const [description, setDescription] = useState('')

  // Performance-based form
  const [csvFile, setCsvFile] = useState(null)
  const [apiToken, setApiToken] = useState('')

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false)
  const [dataClean, setDataClean] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)

  const handleSendAndClean = (e) => {
    e.preventDefault()
    if (!topic.trim()) return

    setDataClean(false)
    setAnalyzing(true)

    // Simulate data cleaning
    setTimeout(() => {
      setDataClean(true)
      setAnalyzing(false)
    }, 1200)
  }

  const handleAnalyzeCSV = () => {
    if (!csvFile) return
    setDataClean(false)
    setAnalyzing(true)
    setTimeout(() => {
      setDataClean(true)
      setAnalyzing(false)
    }, 1500)
  }

  const handleStartAnalysis = () => {
    setAnalyzing(true)
    setTimeout(() => {
      setAnalysisResult({
        predictedEngagement: (Math.random() * 5 + 1).toFixed(1),
        bestTime: ['Salı 20:00', 'Cuma 18:00', 'Cumartesi 21:00', 'Pazar 14:00'][Math.floor(Math.random() * 4)],
        trendFitScore: Math.floor(Math.random() * 30 + 65),
      })
      setStep(2)
      setAnalyzing(false)
    }, 2000)
  }

  const stepLabels = ['1. Data Entry', '2. Results', '3. Recommendations']

  return (
    <div className="max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className={`font-display text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Analysis
          </h1>
          <p className={`mt-1 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>
            İçerik veya performans verilerinizi analiz edin
          </p>
        </div>
        <span className="font-display text-lg font-semibold gradient-text">Trendify</span>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-8">
        {stepLabels.map((label, i) => (
          <button
            key={label}
            onClick={() => {
              if (i + 1 <= step) setStep(i + 1)
            }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${step === i + 1
                ? 'bg-primary-600 text-white'
                : i + 1 < step
                  ? darkMode ? 'bg-dark-700 text-primary-400 cursor-pointer' : 'bg-primary-50 text-primary-600 cursor-pointer'
                  : darkMode ? 'bg-dark-800 text-dark-500' : 'bg-gray-100 text-gray-400'
              }`}
          >
            {label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* STEP 1: Data Entry */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Tab Selector */}
            <div className="flex mb-6">
              <button
                onClick={() => setActiveTab('content')}
                className={`flex-1 py-3 px-6 rounded-l-xl font-medium text-sm transition-all duration-200
                  ${activeTab === 'content'
                    ? 'bg-primary-600 text-white'
                    : darkMode ? 'bg-dark-800 text-dark-400 hover:text-white' : 'bg-gray-100 text-gray-500 hover:text-gray-900'
                  }`}
              >
                <HiOutlineDocumentText className="inline w-4 h-4 mr-2 -mt-0.5" />
                Content-Based
              </button>
              <button
                onClick={() => setActiveTab('performance')}
                className={`flex-1 py-3 px-6 rounded-r-xl font-medium text-sm transition-all duration-200
                  ${activeTab === 'performance'
                    ? 'bg-primary-600 text-white'
                    : darkMode ? 'bg-dark-800 text-dark-400 hover:text-white' : 'bg-gray-100 text-gray-500 hover:text-gray-900'
                  }`}
              >
                <HiOutlineChartBarSquare className="inline w-4 h-4 mr-2 -mt-0.5" />
                Performance-Based
              </button>
            </div>

            {/* Content-Based Form */}
            {activeTab === 'content' && (
              <div className={`${darkMode ? 'card' : 'card-light'}`}>
                <form onSubmit={handleSendAndClean} className="space-y-5">
                  <div className="grid grid-cols-2 gap-5">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                        Topic / Keyword
                      </label>
                      <input
                        type="text"
                        value={topic}
                        onChange={e => setTopic(e.target.value)}
                        placeholder="e.g. Sustainable Fashion"
                        className={darkMode ? 'input-field' : 'input-field-light'}
                      />
                    </div>
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                        Platform
                      </label>
                      <select
                        value={platform}
                        onChange={e => setPlatform(e.target.value)}
                        className={darkMode ? 'input-field' : 'input-field-light'}
                      >
                        {platforms.map(p => (
                          <option key={p} value={p}>{p}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-5">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                        Goal
                      </label>
                      <select
                        value={goal}
                        onChange={e => setGoal(e.target.value)}
                        className={darkMode ? 'input-field' : 'input-field-light'}
                      >
                        {goals.map(g => (
                          <option key={g} value={g}>{g}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                        Language
                      </label>
                      <select
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                        className={darkMode ? 'input-field' : 'input-field-light'}
                      >
                        {languages.map(l => (
                          <option key={l} value={l}>{l}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                      Description (Optional)
                    </label>
                    <textarea
                      value={description}
                      onChange={e => setDescription(e.target.value)}
                      placeholder="Brief context about the post..."
                      rows={3}
                      className={darkMode ? 'input-field resize-none' : 'input-field-light resize-none'}
                    />
                  </div>

                  <button type="submit" disabled={analyzing || !topic.trim()} className="btn-primary disabled:opacity-50">
                    {analyzing ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Cleaning Data...
                      </span>
                    ) : (
                      'Send & Clean Data'
                    )}
                  </button>
                </form>
              </div>
            )}

            {/* Performance-Based Form */}
            {activeTab === 'performance' && (
              <div className={`${darkMode ? 'card' : 'card-light'}`}>
                <div className="space-y-5">
                  {/* CSV Upload */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                      Drop CSV file here or click to upload
                    </label>
                    <label
                      className={`flex flex-col items-center justify-center w-full h-32 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200
                        ${darkMode
                          ? 'border-dark-600 hover:border-primary-500/50 bg-dark-800/30'
                          : 'border-gray-300 hover:border-primary-400 bg-gray-50'
                        }`}
                    >
                      <HiOutlineArrowUpTray className={`w-8 h-8 mb-2 ${darkMode ? 'text-dark-400' : 'text-gray-400'}`} />
                      <span className={`text-sm ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>
                        {csvFile ? csvFile.name : 'CSV dosyası seçin'}
                      </span>
                      <input
                        type="file"
                        accept=".csv"
                        className="hidden"
                        onChange={e => setCsvFile(e.target.files[0] || null)}
                      />
                    </label>
                  </div>

                  {/* API Token */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-dark-300' : 'text-gray-600'}`}>
                      Social API Token (Optional)
                    </label>
                    <input
                      type="text"
                      value={apiToken}
                      onChange={e => setApiToken(e.target.value)}
                      placeholder="Paste token"
                      className={darkMode ? 'input-field' : 'input-field-light'}
                    />
                  </div>

                  <button
                    onClick={handleAnalyzeCSV}
                    disabled={analyzing || !csvFile}
                    className="btn-primary disabled:opacity-50"
                  >
                    {analyzing ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Analyzing CSV...
                      </span>
                    ) : (
                      'Analyze CSV'
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Data Clean Status */}
            {dataClean && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`mt-6 p-4 rounded-xl flex items-center gap-3
                  ${darkMode ? 'bg-green-500/10 border border-green-500/20' : 'bg-green-50 border border-green-200'}`}
              >
                <HiOutlineCheck className="w-5 h-5 text-green-500" />
                <span className={darkMode ? 'text-green-400' : 'text-green-700'}>
                  Data ready for analysis. Clean: OK
                </span>
              </motion.div>
            )}

            {/* Start Analysis Button */}
            {dataClean && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6">
                <button onClick={handleStartAnalysis} disabled={analyzing} className="btn-primary disabled:opacity-50">
                  {analyzing ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Analyzing...
                    </span>
                  ) : (
                    'Start Analysis'
                  )}
                </button>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* STEP 2: Results */}
        {step === 2 && analysisResult && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <div className={`${darkMode ? 'card' : 'card-light'} mb-6`}>
              <h2 className={`font-display text-xl font-semibold mb-6 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Analysis Report
              </h2>

              <div className="grid grid-cols-3 gap-4 mb-6">
                {/* Predicted Engagement */}
                <div className={`p-5 rounded-xl text-center ${darkMode ? 'bg-dark-700/50 border border-dark-600/50' : 'bg-gray-50 border border-gray-200'}`}>
                  <HiOutlineSparkles className="w-6 h-6 mx-auto mb-2 text-primary-400" />
                  <p className={`text-sm mb-1 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>Predicted Engagement</p>
                  <p className={`text-2xl font-bold font-display ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {analysisResult.predictedEngagement}%
                  </p>
                </div>

                {/* Best Time to Post */}
                <div className={`p-5 rounded-xl text-center ${darkMode ? 'bg-dark-700/50 border border-dark-600/50' : 'bg-gray-50 border border-gray-200'}`}>
                  <HiOutlineClock className="w-6 h-6 mx-auto mb-2 text-blue-400" />
                  <p className={`text-sm mb-1 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>Best Time to Post</p>
                  <p className={`text-2xl font-bold font-display ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {analysisResult.bestTime}
                  </p>
                </div>

                {/* Trend Fit Score */}
                <div className={`p-5 rounded-xl text-center ${darkMode ? 'bg-dark-700/50 border border-dark-600/50' : 'bg-gray-50 border border-gray-200'}`}>
                  <HiOutlineFire className="w-6 h-6 mx-auto mb-2 text-orange-400" />
                  <p className={`text-sm mb-1 ${darkMode ? 'text-dark-400' : 'text-gray-500'}`}>Trend Fit Score</p>
                  <p className={`text-2xl font-bold font-display ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {analysisResult.trendFitScore}/100
                  </p>
                </div>
              </div>

              {/* Status message */}
              <div className={`p-4 rounded-xl ${darkMode ? 'bg-primary-500/10 border border-primary-500/20' : 'bg-primary-50 border border-primary-200'}`}>
                <p className={`text-sm ${darkMode ? 'text-primary-300' : 'text-primary-700'}`}>
                  Analysis complete. Based on current trends, your topic has high potential.
                </p>
              </div>
            </div>

            {/* Navigate to AI Chat */}
            <button
              onClick={() => navigate('/app/chat')}
              className="btn-primary flex items-center gap-2"
            >
              Go to AI Chat for Recommendations
              <HiOutlineArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
