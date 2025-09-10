import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AnalysisRequest {
  url: string
}

export interface AnalysisJobResponse {
  job_id: string
  url: string
  status: string
  created_at: string
}

export interface AnalysisStatusResponse {
  job_id: string
  url: string
  status: string
  progress: number
  created_at: string
  updated_at: string
  completed_at?: string
  error_message?: string
}

export interface MessagingScores {
  clarity: number
  consistency: number
  differentiation: number
  proof: number
  cta_strength: number
  audience_fit: number
  overall: number
}

export interface MessagingAnalysis {
  primary_message: string
  target_audience: string
  value_proposition: string
  tone_and_voice: string
  key_themes: string[]
  strengths: string[]
  weaknesses: string[]
}

export interface AnalysisResultResponse {
  job_id: string
  url: string
  status: string
  content_summary?: string
  messaging_analysis?: MessagingAnalysis
  scores?: MessagingScores
  quick_wins?: string[]
  completed_at?: string
  error_message?: string
}

export const analysisApi = {
  // Start website analysis
  startAnalysis: async (data: AnalysisRequest): Promise<AnalysisJobResponse> => {
    const response = await api.post('/analysis/reflect', data)
    return response.data
  },

  // Get analysis status
  getAnalysisStatus: async (jobId: string): Promise<AnalysisStatusResponse> => {
    const response = await api.get(`/analysis/reflect/${jobId}/status`)
    return response.data
  },

  // Get analysis result
  getAnalysisResult: async (jobId: string): Promise<AnalysisResultResponse> => {
    const response = await api.get(`/analysis/reflect/${jobId}/result`)
    return response.data
  },

  // Get crawled pages
  getCrawledPages: async (jobId: string): Promise<any> => {
    const response = await api.get(`/analysis/reflect/${jobId}/pages`)
    return response.data
  },
}

export default api
