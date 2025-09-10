'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { analysisApi } from '@/lib/api'
import { getProgressMessage } from '@/lib/utils'
import { AnalysisData } from '@/app/page'

interface AnalysisProgressProps {
  data: AnalysisData
  onComplete: (result: any) => void
  onError: (error: string) => void
}

export function AnalysisProgress({ data, onComplete, onError }: AnalysisProgressProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [isPolling, setIsPolling] = useState(true)

  useEffect(() => {
    let pollInterval: NodeJS.Timeout

    const pollStatus = async () => {
      try {
        const status = await analysisApi.getAnalysisStatus(data.jobId)
        
        setProgress(status.progress)
        setCurrentStep(getProgressMessage(status.progress))

        if (status.status === 'completed') {
          setIsPolling(false)
          
          // Get the full result
          try {
            const result = await analysisApi.getAnalysisResult(data.jobId)
            onComplete(result)
          } catch (resultError) {
            console.error('Error fetching result:', resultError)
            onError('Failed to fetch analysis result')
          }
          
        } else if (status.status === 'failed') {
          setIsPolling(false)
          onError(status.error_message || 'Analysis failed')
        }
        
      } catch (error) {
        console.error('Polling error:', error)
        setIsPolling(false)
        onError('Failed to check analysis status')
      }
    }

    if (isPolling) {
      // Poll immediately, then every 2 seconds
      pollStatus()
      pollInterval = setInterval(pollStatus, 2000)
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [data.jobId, isPolling, onComplete, onError])

  const steps = [
    { name: 'Crawl', description: 'Scanning your website pages', threshold: 20 },
    { name: 'Parse', description: 'Extracting content and structure', threshold: 40 },
    { name: 'Analyze', description: 'AI analyzing your messaging', threshold: 80 },
    { name: 'Reflect', description: 'Generating insights and scores', threshold: 100 }
  ]

  return (
    <div className="max-w-2xl mx-auto">
      {/* Mirror Animation */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="relative mx-auto w-48 h-48 mb-12"
      >
        <div className="mirror-frame w-full h-full">
          <div className="mirror-surface">
            {/* Animated Progress Ring */}
            <motion.div
              className="absolute inset-4 rounded-full border-4 border-primary/20"
              style={{
                background: `conic-gradient(from 0deg, hsl(var(--primary)) ${progress * 3.6}deg, transparent ${progress * 3.6}deg)`
              }}
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            />
            
            {/* Center Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Loader2 className="w-8 h-8 text-primary" />
              </motion.div>
              <div className="text-2xl font-bold text-primary mt-2">
                {progress}%
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Progress Info */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass-effect rounded-2xl p-8 space-y-8"
      >
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Analyzing Your Website</h2>
          <p className="text-muted-foreground">
            Reflecting on: <span className="text-primary font-medium">{data.url}</span>
          </p>
        </div>

        {/* Progress Bar */}
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} className="h-3" />
          <p className="text-sm text-center text-muted-foreground">
            {currentStep}
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {steps.map((step, index) => {
            const isActive = progress >= step.threshold - 20 && progress < step.threshold
            const isCompleted = progress >= step.threshold
            
            return (
              <motion.div
                key={step.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className={`text-center space-y-2 p-3 rounded-lg transition-colors ${
                  isActive ? 'bg-primary/10 border border-primary/20' : 
                  isCompleted ? 'bg-green-500/10 border border-green-500/20' : 
                  'bg-muted/20'
                }`}
              >
                <div className="flex justify-center">
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : isActive ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-6 h-6 text-primary" />
                    </motion.div>
                  ) : (
                    <div className="w-6 h-6 rounded-full border-2 border-muted-foreground/30" />
                  )}
                </div>
                <div>
                  <h3 className={`font-semibold text-sm ${
                    isActive ? 'text-primary' : 
                    isCompleted ? 'text-green-500' : 
                    'text-muted-foreground'
                  }`}>
                    {step.name}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Estimated Time */}
        <div className="text-center text-sm text-muted-foreground">
          <p>This usually takes 2-3 minutes depending on your website size</p>
        </div>
      </motion.div>
    </div>
  )
}
