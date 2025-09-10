'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MirrorSection } from '@/components/mirror-section'
import { ProcessingSection } from '@/components/processing-section'
import { SummarySection } from '@/components/summary-section'
import { Footer } from '@/components/footer'

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

  const handleAnalysisStart = (data: AnalysisData) => {
    setAnalysisData(data)
    setAnalysisState('processing')
  }

  const handleAnalysisComplete = (result: any) => {
    setAnalysisData(prev => prev ? { ...prev, result } : null)
    setAnalysisState('completed')
  }

  const handleAnalysisError = () => {
    setAnalysisData(prev => prev ? { ...prev } : null)
    setAnalysisState('error')
  }

  const handleReset = () => {
    setAnalysisState('idle')
    setAnalysisData(null)
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
