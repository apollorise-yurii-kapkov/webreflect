'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { analysisApi } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { AnalysisData } from '@/app/page'

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
    <div className="min-h-screen flex items-center justify-center p-8 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900" />
      
      {/* Animated background particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white/10 rounded-full"
            animate={{
              x: [0, Math.random() * 100 - 50],
              y: [0, Math.random() * 100 - 50],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
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
        {/* Mirror container */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="relative"
        >
          {/* Main mirror */}
          <div className="relative w-full h-[600px] rounded-3xl overflow-hidden bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-xl border border-white/10">
            {/* Blurred background image effect */}
            <div className="absolute inset-4 rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 blur-2xl" />
            
            {/* Shimmer overlay */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
              animate={{
                x: [-100, 400],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "linear",
              }}
            />

            {/* Content overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
              {/* Title */}
              <motion.h1
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.8 }}
                className="text-5xl font-light text-white mb-4 tracking-wide"
              >
                Website Mirror
              </motion.h1>

              {/* Description */}
              <motion.p
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.7, duration: 0.8 }}
                className="text-xl text-gray-300 mb-12 max-w-2xl leading-relaxed"
              >
                See what your website truly reflects. Get an objective analysis of your site&apos;s message and content.
              </motion.p>

              {/* Input form */}
              <motion.form
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.9, duration: 0.8 }}
                onSubmit={handleSubmit}
                className="w-full max-w-md"
              >
                <div className="relative">
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Enter website URL..."
                    disabled={isLoading}
                    className="w-full px-6 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent transition-all duration-300"
                  />
                  <motion.button
                    type="submit"
                    disabled={isLoading || !url.trim()}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="absolute right-2 top-2 bottom-2 px-6 bg-white/20 hover:bg-white/30 disabled:bg-white/10 disabled:cursor-not-allowed rounded-xl text-white font-medium transition-all duration-300 backdrop-blur-sm"
                  >
                    {isLoading ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                      />
                    ) : (
                      'Analyze'
                    )}
                  </motion.button>
                </div>
              </motion.form>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
