'use client'

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { analysisApi } from '@/lib/api'
import { AnalysisData } from '@/app/page'

interface ProcessingSectionProps {
  data: AnalysisData
  onComplete: (result: any) => void
  onError: () => void
}

const processingSteps = [
  { id: 'crawling', label: 'Scanning website pages', duration: 3000 },
  { id: 'extracting', label: 'Extracting content', duration: 2000 },
  { id: 'analyzing', label: 'Analyzing messaging', duration: 4000 },
  { id: 'generating', label: 'Generating summary', duration: 2000 },
]

export function ProcessingSection({ data, onComplete, onError }: ProcessingSectionProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let interval: NodeJS.Timeout

    const pollStatus = async () => {
      try {
        const status = await analysisApi.getAnalysisStatus(data.jobId)
        
        if (status.status === 'completed' && status.result) {
          onComplete(status.result)
          return
        }
        
        if (status.status === 'failed') {
          onError()
          return
        }

        // Update progress based on status
        if (status.progress !== undefined) {
          setProgress(status.progress)
          const stepIndex = Math.floor((status.progress / 100) * processingSteps.length)
          setCurrentStep(Math.min(stepIndex, processingSteps.length - 1))
        }
      } catch (error) {
        console.error('Error polling status:', error)
        onError()
      }
    }

    // Start polling
    interval = setInterval(pollStatus, 2000)
    pollStatus() // Initial call

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [data.jobId, onComplete, onError])

  return (
    <div className="min-h-screen flex items-center justify-center p-8 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900" />
      
      {/* Animated particles */}
      <div className="absolute inset-0">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400/30 rounded-full"
            animate={{
              x: [0, Math.random() * 200 - 100],
              y: [0, Math.random() * 200 - 100],
              opacity: [0, 1, 0],
              scale: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 4 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-4xl">
        {/* Processing mirror */}
        <motion.div
          initial={{ scale: 1 }}
          animate={{ 
            scale: [1, 1.02, 1],
            rotateY: [0, 2, -2, 0],
          }}
          transition={{ 
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="relative"
        >
          <div className="relative w-full h-[600px] rounded-3xl overflow-hidden bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-xl border border-white/10">
            {/* Dynamic background based on progress */}
            <motion.div 
              className="absolute inset-4 rounded-2xl blur-2xl"
              animate={{
                background: [
                  'linear-gradient(45deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2))',
                  'linear-gradient(45deg, rgba(147, 51, 234, 0.2), rgba(236, 72, 153, 0.2))',
                  'linear-gradient(45deg, rgba(236, 72, 153, 0.2), rgba(59, 130, 246, 0.2))',
                ]
              }}
              transition={{ duration: 3, repeat: Infinity }}
            />
            
            {/* Scanning effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/20 to-transparent"
              animate={{
                x: [-200, 600],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear",
              }}
            />

            {/* Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
              {/* URL being analyzed */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
              >
                <p className="text-gray-400 text-sm mb-2">Analyzing</p>
                <p className="text-white text-lg font-medium">{data.url}</p>
              </motion.div>

              {/* Progress circle */}
              <div className="relative w-32 h-32 mb-8">
                <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="2"
                    fill="none"
                  />
                  <motion.circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke="rgba(59, 130, 246, 0.8)"
                    strokeWidth="2"
                    fill="none"
                    strokeLinecap="round"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: progress / 100 }}
                    transition={{ duration: 0.5 }}
                    style={{
                      strokeDasharray: "283",
                      strokeDashoffset: 283 - (283 * progress) / 100,
                    }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-white text-xl font-medium">{Math.round(progress)}%</span>
                </div>
              </div>

              {/* Current step */}
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="text-center"
              >
                <p className="text-blue-400 text-lg font-medium mb-2">
                  {processingSteps[currentStep]?.label}
                </p>
                <div className="flex justify-center space-x-1">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity }}
                    className="w-2 h-2 bg-blue-400 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 bg-blue-400 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 bg-blue-400 rounded-full"
                  />
                </div>
              </motion.div>

              {/* Steps indicator */}
              <div className="mt-12 flex justify-center space-x-4">
                {processingSteps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`w-3 h-3 rounded-full transition-all duration-500 ${
                      index <= currentStep 
                        ? 'bg-blue-400 shadow-lg shadow-blue-400/50' 
                        : 'bg-white/20'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
