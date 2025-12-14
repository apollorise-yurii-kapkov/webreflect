'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { analysisApi } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { AnalysisData } from '@/app/page'
import { CSSMirror } from './css-mirror'

interface MirrorSectionProps {
  onAnalysisStart: (data: AnalysisData) => void
}

export function MirrorSection({ onAnalysisStart }: MirrorSectionProps) {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const formatUrl = (input: string): string => {
    const trimmed = input.trim()
    if (!trimmed) return ''
    
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      return trimmed
    }
    return `https://${trimmed}`
  }

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    const formattedUrl = formatUrl(url.trim())
    if (!isValidUrl(formattedUrl)) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid website URL",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      const response = await analysisApi.startAnalysis({ url: formattedUrl })
      onAnalysisStart({
        jobId: response.job_id,
        url: response.url,
        status: response.status,
        progress: 0
      })
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to start analysis",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  return (
    <div className="h-[100dvh] relative overflow-hidden bg-black">
      {/* Background mirror effect */}
      <CSSMirror>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="text-center max-w-2xl mx-auto flex flex-col items-center"
        >
          {/* Title */}
          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="text-3xl sm:text-4xl md:text-5xl font-light text-white mb-4 tracking-wide px-4"
          >
            Your Website’s Reflection in Others Eyes
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="text-base sm:text-lg md:text-xl text-gray-300 mb-8 sm:mb-12 leading-relaxed text-center px-4"
          >
            Paste your URL and let AI reflect what visitors truly see and hear — in one clear, objective messaging audit.
          </motion.p>

          {/* Input form */}
          <motion.form
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.8 }}
            onSubmit={handleSubmit}
            className="w-full max-w-lg mx-auto px-4"
          >
            <div className="relative">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter website URL..."
                disabled={isLoading}
                className="w-full px-4 sm:px-6 py-3 sm:py-4 bg-black/40 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent transition-all duration-300 text-sm sm:text-base pr-28 sm:pr-36"
              />
              <motion.button
                type="submit"
                disabled={isLoading || !url.trim()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="absolute right-2 top-2 bottom-2 px-3 sm:px-6 bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed rounded-xl text-white font-medium transition-all duration-300 backdrop-blur-sm text-xs sm:text-base"
              >
                {isLoading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                ) : (
                  'Show me'
                )}
              </motion.button>
            </div>
            <div className="mt-4 text-center">
              <span className="text-xs text-white/40 font-light tracking-wide">
                Daily limit: 10 reflections per day
              </span>
            </div>
          </motion.form>
        </motion.div>
      </CSSMirror>
    </div>
  )
}
