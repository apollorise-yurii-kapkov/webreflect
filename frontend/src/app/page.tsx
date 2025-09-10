'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MirrorSection } from '@/components/mirror-section'
import { ProcessingSection } from '@/components/processing-section'
import { SummarySection } from '@/components/summary-section'
import { Footer } from '@/components/footer'
import { analysisApi } from '@/lib/api'

export type AnalysisState = 'idle' | 'processing' | 'completed' | 'error'

export interface AnalysisData {
  jobId: string
  url: string
  status: string
  progress: number
  result?: any
}

export default function Home() {
  const [analysisState, setAnalysisState] = useState<AnalysisState>('idle')
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)

  // Check for id in URL path on component mount
  useEffect(() => {
    const path = window.location.pathname
    const id = path.substring(1) // Remove leading slash
    
    if (id && id.length > 0) {
      // Load analysis data from shared report
      loadSharedReport(id)
    }
  }, [])

  const loadSharedReport = async (id: string) => {
    try {
      // Try to load shared report - this will fail if not shared
      const statusResponse = await analysisApi.getSharedReport(id)
      
      const analysisData: AnalysisData = {
        jobId: statusResponse.job_id,
        url: statusResponse.url,
        status: statusResponse.status,
        progress: statusResponse.progress,
        result: statusResponse.result
      }
      
      setAnalysisData(analysisData)
      
      if (statusResponse.status === 'completed' && statusResponse.result) {
        setAnalysisState('completed')
      } else if (statusResponse.status === 'failed') {
        setAnalysisState('error')
      } else {
        setAnalysisState('processing')
      }
    } catch (error) {
      console.error('Failed to load shared report:', error)
      setAnalysisState('error')
    }
  }

  const handleAnalysisStart = (data: AnalysisData) => {
    setAnalysisData(data)
    setAnalysisState('processing')
    
    // Don't add URL parameter during analysis - only when sharing
  }

  const handleAnalysisComplete = (result: any) => {
    setAnalysisData(prev => prev ? { ...prev, result } : null)
    setAnalysisState('completed')
    
    // Update URL with job ID when analysis completes
    if (analysisData?.jobId) {
      window.history.pushState({}, '', `/${analysisData.jobId}`)
    }
  }

  const handleAnalysisError = () => {
    setAnalysisData(prev => prev ? { ...prev } : null)
    setAnalysisState('error')
  }

  const handleReset = () => {
    setAnalysisState('idle')
    setAnalysisData(null)
    
    // Clear id from URL - go back to root
    window.history.pushState({}, '', '/')
  }

  return (
    <div className="min-h-screen bg-black">
      <AnimatePresence mode="wait">
        {analysisState === 'idle' && (
          <motion.div
            key="mirror"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <MirrorSection onAnalysisStart={handleAnalysisStart} />
          </motion.div>
        )}

        {analysisState === 'processing' && analysisData && (
          <motion.div
            key="processing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <ProcessingSection 
              data={analysisData}
              onComplete={handleAnalysisComplete}
              onError={handleAnalysisError}
            />
          </motion.div>
        )}

        {(analysisState === 'completed' || analysisState === 'error') && analysisData && (
          <motion.div
            key="summary"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <SummarySection 
              data={analysisData}
              onReset={handleReset}
              isError={analysisState === 'error'}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <Footer />
    </div>
  )
}
