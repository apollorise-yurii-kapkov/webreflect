'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { SummarySection } from '@/components/summary-section'
import { Footer } from '@/components/footer'
import { analysisApi } from '@/lib/api'

interface AnalysisData {
  jobId: string
  url: string
  status: string
  progress: number
  result?: any
}

export default function ReportPage() {
  const params = useParams()
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const loadReport = async () => {
      try {
        const id = params.id as string
        if (!id) return

        // Load shared report
        const statusResponse = await analysisApi.getSharedReport(id)
        
        const data: AnalysisData = {
          jobId: statusResponse.job_id,
          url: statusResponse.url,
          status: statusResponse.status,
          progress: statusResponse.progress,
          result: statusResponse.result
        }
        
        setAnalysisData(data)
      } catch (error) {
        console.error('Failed to load report:', error)
        setError(true)
      } finally {
        setLoading(false)
      }
    }

    loadReport()
  }, [params.id])

  const handleReset = () => {
    window.location.href = '/'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading report...</div>
      </div>
    )
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 mb-4">Report not found</div>
          <button 
            onClick={handleReset}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg"
          >
            Go Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <SummarySection 
      data={analysisData} 
      onReset={handleReset}
    />
  )
}
