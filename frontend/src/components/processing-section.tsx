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
    let consecutiveErrors = 0
    const MAX_RETRIES = 5

    const pollStatus = async () => {
      try {
        const status = await analysisApi.getAnalysisStatus(data.jobId)

        // Reset error counter on success
        consecutiveErrors = 0

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
        consecutiveErrors++

        // Only trigger error state if we've failed multiple times in a row
        if (consecutiveErrors >= MAX_RETRIES) {
          onError()
        }
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
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Animated particles background */}
      <div className="absolute inset-0">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400/20 rounded-full"
            animate={{
              x: [0, Math.random() * 300 - 150],
              y: [0, Math.random() * 300 - 150],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
            }}
            transition={{
              duration: Math.random() * 6 + 3,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 flex items-center justify-center p-8 min-h-screen">
        <div className="w-full max-w-4xl">
          {/* Processing Mirror */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{
              scale: 1,
              opacity: 1,
            }}
            transition={{
              duration: 0.8,
              ease: "easeOut"
            }}
            className="relative"
          >
            <div className="relative w-full h-[780px] rounded-3xl overflow-hidden bg-gradient-to-br from-gray-800/30 to-gray-900/30 backdrop-blur-xl border border-white/20 shadow-2xl">
              {/* Dynamic scanning effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/10 to-transparent"
                animate={{
                  x: [-300, 700],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />

              {/* Pulsing glow effect */}
              <motion.div
                className="absolute inset-4 rounded-2xl blur-3xl"
                animate={{
                  background: [
                    'linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1))',
                    'linear-gradient(45deg, rgba(147, 51, 234, 0.2), rgba(236, 72, 153, 0.1))',
                    'linear-gradient(45deg, rgba(236, 72, 153, 0.1), rgba(59, 130, 246, 0.2))',
                  ]
                }}
                transition={{ duration: 4, repeat: Infinity }}
              />

              {/* Content */}
              <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
                {/* URL being analyzed */}
                <motion.div
                  initial={{ opacity: 0, y: -30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mb-12"
                >
                  <motion.p
                    className="text-gray-300 text-sm mb-3 tracking-wider uppercase"
                    animate={{ opacity: [0.7, 1, 0.7] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    Analyzing Website
                  </motion.p>
                  <p className="text-white text-xl font-light max-w-2xl break-all">{data.url}</p>
                </motion.div>

                {/* Enhanced Progress Circle */}
                <div className="relative w-40 h-40 mb-12">
                  {/* Outer glow ring */}
                  <motion.div
                    className="absolute inset-0 rounded-full"
                    animate={{
                      boxShadow: [
                        '0 0 20px rgba(59, 130, 246, 0.3)',
                        '0 0 40px rgba(59, 130, 246, 0.5)',
                        '0 0 20px rgba(59, 130, 246, 0.3)',
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />

                  <svg className="w-40 h-40 transform -rotate-90" viewBox="0 0 100 100">
                    {/* Background circle */}
                    <circle
                      cx="50"
                      cy="50"
                      r="42"
                      stroke="rgba(255,255,255,0.1)"
                      strokeWidth="1.5"
                      fill="none"
                    />
                    {/* Progress circle */}
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="42"
                      stroke="url(#progressGradient)"
                      strokeWidth="2"
                      fill="none"
                      strokeLinecap="round"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: progress / 100 }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      style={{
                        strokeDasharray: "264",
                        strokeDashoffset: 264 - (264 * progress) / 100,
                      }}
                    />
                    <defs>
                      <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="rgba(59, 130, 246, 0.9)" />
                        <stop offset="50%" stopColor="rgba(147, 51, 234, 0.9)" />
                        <stop offset="100%" stopColor="rgba(236, 72, 153, 0.9)" />
                      </linearGradient>
                    </defs>
                  </svg>

                  {/* Progress text */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.span
                      className="text-white text-2xl font-light mb-1"
                      key={progress}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      {Math.round(progress)}%
                    </motion.span>
                    <span className="text-gray-400 text-xs tracking-wider uppercase">Complete</span>
                  </div>
                </div>

                {/* Current step with enhanced animation */}
                <motion.div
                  key={currentStep}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -30 }}
                  transition={{ duration: 0.5 }}
                  className="text-center mb-8"
                >
                  <motion.p
                    className="text-blue-300 text-xl font-light mb-4"
                    animate={{ opacity: [0.8, 1, 0.8] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    {processingSteps[currentStep]?.label}
                  </motion.p>

                  {/* Animated dots */}
                  <div className="flex justify-center space-x-2">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{
                          scale: [1, 1.4, 1],
                          opacity: [0.5, 1, 0.5]
                        }}
                        transition={{
                          duration: 1.2,
                          repeat: Infinity,
                          delay: i * 0.2
                        }}
                        className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full"
                      />
                    ))}
                  </div>
                </motion.div>

                {/* Enhanced Steps indicator */}
                <div className="flex justify-center space-x-6">
                  {processingSteps.map((step, index) => (
                    <motion.div
                      key={step.id}
                      className="flex flex-col items-center space-y-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <motion.div
                        className={`w-4 h-4 rounded-full transition-all duration-700 ${index <= currentStep
                            ? 'bg-gradient-to-r from-blue-400 to-purple-400 shadow-lg'
                            : 'bg-white/20'
                          }`}
                        animate={index === currentStep ? {
                          scale: [1, 1.2, 1],
                          boxShadow: [
                            '0 0 10px rgba(59, 130, 246, 0.5)',
                            '0 0 20px rgba(59, 130, 246, 0.8)',
                            '0 0 10px rgba(59, 130, 246, 0.5)',
                          ]
                        } : {}}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      />
                      <span className={`text-xs transition-colors duration-500 ${index <= currentStep ? 'text-white' : 'text-gray-500'
                        }`}>
                        {step.label.split(' ')[0]}
                      </span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
