'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { AnalysisData } from '@/app/page'

interface SummarySectionProps {
  data: AnalysisData
  onReset: () => void
  isError?: boolean
}

export function SummarySection({ data, onReset, isError }: SummarySectionProps) {
  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 bg-black">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-md"
        >
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-red-500 rounded-full flex items-center justify-center">
              <span className="text-red-500 text-xl">!</span>
            </div>
          </div>
          <h2 className="text-2xl font-light text-white mb-4">Analysis Failed</h2>
          <p className="text-gray-400 mb-8">
            Unable to analyze the website. Please try again with a different URL.
          </p>
          <button
            onClick={onReset}
            className="px-8 py-3 bg-white/10 hover:bg-white/20 text-white rounded-2xl transition-all duration-300 backdrop-blur-sm border border-white/20"
          >
            Try Again
          </button>
        </motion.div>
      </div>
    )
  }

  const summary = data.result?.content_summary || ''
  const messaging = data.result?.messaging_analysis || ''

  // Combine and format the analysis text
  const analysisText = `${summary}\n\n${messaging}`.trim()

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky top-0 z-10 bg-black/80 backdrop-blur-sm border-b border-white/10"
      >
        <div className="max-w-4xl mx-auto px-8 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-light text-white">Website Analysis</h1>
            <p className="text-gray-400 text-sm mt-1">{data.url}</p>
          </div>
          <button
            onClick={onReset}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all duration-300 backdrop-blur-sm border border-white/20 text-sm"
          >
            New Analysis
          </button>
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="prose prose-invert prose-lg max-w-none"
        >
          {/* Summary container */}
          <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/50 backdrop-blur-sm rounded-3xl p-12 border border-white/10">
            {analysisText ? (
              <div className="space-y-6">
                {analysisText.split('\n\n').map((paragraph, index) => (
                  <motion.p
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="text-gray-300 leading-relaxed text-lg"
                  >
                    {paragraph}
                  </motion.p>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gray-700/50 flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-gray-500 rounded-full animate-spin border-t-transparent" />
                </div>
                <p className="text-gray-400">Processing analysis results...</p>
              </div>
            )}
          </div>

          {/* Footer info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-12 text-center"
          >
            <p className="text-gray-500 text-sm">
              This analysis provides an objective summary of the website&apos;s content and messaging without subjective scoring or recommendations.
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
