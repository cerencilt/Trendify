// Mock analysis history data
export const mockAnalyses = [
  {
    id: 1,
    date: '2025-01-15',
    platform: 'Instagram',
    topic: 'Summer vibes',
    predictedEngagement: 1.200,
    bestTime: 'Cuma 18:00',
    trendFitScore: 78,
    status: 'completed',
    type: 'content',
  },
  {
    id: 2,
    date: '2025-01-16',
    platform: 'TikTok',
    topic: 'Dance challenge',
    predictedEngagement: 4.500,
    bestTime: 'Cumartesi 20:00',
    trendFitScore: 92,
    status: 'completed',
    type: 'content',
  },
  {
    id: 3,
    date: '2025-01-17',
    platform: 'YouTube',
    topic: 'Tech review',
    predictedEngagement: 2.800,
    bestTime: 'Pazar 14:00',
    trendFitScore: 65,
    status: 'completed',
    type: 'performance',
  },
  {
    id: 4,
    date: '2025-01-18',
    platform: 'Instagram',
    topic: 'Moda trendleri',
    predictedEngagement: 3.100,
    bestTime: 'Salı 20:30',
    trendFitScore: 85,
    status: 'completed',
    type: 'content',
  },
]

// Mock engagement heatmap data (hour x day)
export const mockHeatmapData = [
  { day: 'Pazartesi', h08: 12, h10: 25, h12: 45, h14: 38, h16: 52, h18: 78, h20: 95, h22: 60 },
  { day: 'Salı', h08: 15, h10: 30, h12: 50, h14: 42, h16: 58, h18: 85, h20: 98, h22: 55 },
  { day: 'Çarşamba', h08: 10, h10: 22, h12: 40, h14: 35, h16: 48, h18: 70, h20: 88, h22: 50 },
  { day: 'Perşembe', h08: 18, h10: 28, h12: 48, h14: 40, h16: 55, h18: 80, h20: 92, h22: 58 },
  { day: 'Cuma', h08: 20, h10: 35, h12: 55, h14: 50, h16: 65, h18: 90, h20: 100, h22: 70 },
  { day: 'Cumartesi', h08: 25, h10: 40, h12: 60, h14: 55, h16: 70, h18: 88, h20: 95, h22: 75 },
  { day: 'Pazar', h08: 22, h10: 38, h12: 58, h14: 52, h16: 62, h18: 82, h20: 90, h22: 65 },
]

// Mock platform comparison data
export const mockPlatformData = [
  { name: 'Instagram', engagement: 3.2, reach: 4500, growth: 12 },
  { name: 'TikTok', engagement: 5.8, reach: 12000, growth: 28 },
  { name: 'YouTube', engagement: 2.1, reach: 3200, growth: 8 },
]

// Mock chat messages
export const mockChatMessages = [
  {
    id: 1,
    role: 'assistant',
    content: 'Merhaba! Analiz verilerinize göre size yardımcı olabilirim. Hashtag, paylaşım zamanı, müzik veya açıklama önerisi almak ister misiniz?',
  },
]

// Mock trending hashtags
export const mockTrendingHashtags = [
  '#fashiontrends', '#sustainablefashion', '#ootd', '#styleinspo',
  '#trendalert', '#modatrend', '#fashionweek', '#streetstyle',
]

// Mock recommendations
export const mockRecommendations = [
  {
    id: 1,
    analysisId: 1,
    type: 'time',
    title: 'En İyi Paylaşım Zamanı',
    description: 'Cuma günleri 18:00-20:00 arası paylaşım yapmanızı öneriyoruz.',
    reason: 'Geçmiş verilerinizde bu zaman diliminde %35 daha yüksek etkileşim oranı gözlemlendi.',
    score: 92,
  },
  {
    id: 2,
    analysisId: 1,
    type: 'hashtag',
    title: 'Önerilen Hashtag\'ler',
    description: '#summervibes #yaz #plajhayatı #tatilmodası #güneş',
    reason: 'Bu hashtag\'ler benzer içeriklerde son 7 günde %22 daha fazla keşfet görünürlüğü sağladı.',
    score: 85,
  },
  {
    id: 3,
    analysisId: 1,
    type: 'music',
    title: 'Müzik Önerisi',
    description: 'Trending ses: "Espresso - Sabrina Carpenter" veya "Birds of a Feather - Billie Eilish"',
    reason: 'Bu sesler Instagram Reels\'de şu an en yüksek etkileşim alan trend sesler arasında.',
    score: 78,
  },
]

export const platforms = ['Instagram', 'TikTok', 'YouTube']
export const goals = ['Etkileşim (Engagement)', 'Erişim (Reach)', 'Takipçi Artışı (Growth)', 'Marka Bilinirliği']
export const languages = ['Türkçe (TR)', 'İngilizce (EN)', 'Almanca (DE)', 'Fransızca (FR)']
