import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

const api = axios.create({
  baseURL: `${API_BASE_URL}/v1`,
  timeout: 30000,
  withCredentials: true, // Enable cookies for rate limiting
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + btoa('admin:secure_password_2024'),
  },
})

// Custom error class with user-friendly message
export class ApiError extends Error {
  status: number
  detail: string
  
  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

// Interceptor to transform errors into ApiError with proper messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status || 0
    let detail = 'Failed to connect to server. Please try again.'
    
    // Extract detail from response
    const data = error.response?.data
    if (data) {
      if (typeof data === 'string') {
        try {
          const parsed = JSON.parse(data)
          detail = parsed.detail || detail
        } catch {
          detail = data
        }
      } else if (data.detail) {
        detail = data.detail
      }
    }
    
    // Create ApiError with extracted detail
    const apiError = new ApiError(status, detail)
    // Preserve original response data for rate limit info
    ;(apiError as any).response = error.response
    
    return Promise.reject(apiError)
  }
)

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
  result?: {
    content_summary?: string
    messaging_analysis?: MessagingAnalysis
    scores?: MessagingScores
    quick_wins?: string[]
  }
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

  // Share analysis report (makes it publicly accessible)
  shareReport: async (jobId: string): Promise<{ shared: boolean }> => {
    const response = await api.post(`/analysis/reflect/${jobId}/share`)
    return response.data
  },

  // Get shared report (publicly accessible)
  getSharedReport: async (jobId: string): Promise<AnalysisStatusResponse> => {
    const response = await api.get(`/analysis/shared/${jobId}`)
    return response.data
  },
}

export default api
