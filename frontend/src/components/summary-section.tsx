'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { AnalysisResult } from './analysis-result'
import { Copy, Share2, Download } from 'lucide-react'

interface AnalysisData {
  jobId: string
  url: string
  status: string
  progress: number
  result?: any
}

interface SummarySectionProps {
  data: AnalysisData
  onReset: () => void
  isError?: boolean
}

export function SummarySection({ data, onReset, isError }: SummarySectionProps) {
  const [copySuccess, setCopySuccess] = useState(false)
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

  // Check if we have complete analysis results with scores
  const hasCompleteResults = data.result?.scores && data.result?.messaging_analysis
  
  // Debug: log the data structure
  console.log('Analysis data:', data)
  console.log('Has complete results:', hasCompleteResults)
  console.log('Scores:', data.result?.scores)
  console.log('Messaging analysis:', data.result?.messaging_analysis)

  // Show AnalysisResult only if we have complete results with scores
  if (hasCompleteResults) {
    // Show the full analysis result with scores and buttons
    return (
      <div className="min-h-screen bg-black p-8">
        <AnalysisResult data={data} onReset={onReset} />
      </div>
    )
  }

  // Fallback to simple summary view for incomplete results
  const summary = data.result?.content_summary || ''
  const messaging = data.result?.messaging_analysis || ''
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
            <h1 className="text-2xl font-light text-white">Website Reflection</h1>
            <p className="text-gray-400 text-sm mt-1">{data.url}</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Share/Copy/Download buttons */}
            <button
              onClick={async () => {
                try {
                  const reportText = `Website Analysis Report\n\nURL: ${data.url}\n\n${analysisText}`
                  await navigator.clipboard.writeText(reportText)
                  setCopySuccess(true)
                  setTimeout(() => setCopySuccess(false), 2000)
                } catch (error) {
                  console.error('Failed to copy:', error)
                }
              }}
              className="px-3 py-2 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20 text-sm flex items-center gap-2"
            >
              <Copy className="w-4 h-4" />
              {copySuccess ? 'Copied' : 'Copy'}
            </button>
            
            <button
              onClick={async () => {
                try {
                  if (data.jobId) {
                    // Share the report
                    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
                    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reflect/${data.jobId}/share`, {
                      method: 'POST',
                      headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa('admin:secure_password_2024')
                      }
                    })
                    
                    if (response.ok) {
                      const shareUrl = `${window.location.origin}/${data.jobId}`
                      
                      if (navigator.share) {
                        await navigator.share({
                          title: 'Website Analysis Report',
                          text: 'Check out this website analysis report',
                          url: shareUrl
                        })
                      } else {
                        await navigator.clipboard.writeText(shareUrl)
                      }
                    }
                  }
                } catch (error) {
                  console.error('Failed to share:', error)
                }
              }}
              className="px-3 py-2 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20 text-sm flex items-center gap-2"
            >
              <Share2 className="w-4 h-4" />
              Share
            </button>
            
            <button
              onClick={async () => {
                try {
                  const { jsPDF } = await import('jspdf')
                  const pdf = new jsPDF()
                  const pageHeight = pdf.internal.pageSize.height
                  const margin = 10
                  const maxY = pageHeight - 30
                  let yPos = 30
                  
                  // Function to add text with page breaks
                  const addTextWithBreaks = (text: string, fontSize: number = 12, isBold: boolean = false) => {
                    pdf.setFontSize(fontSize)
                    pdf.setFont('helvetica', isBold ? 'bold' : 'normal')
                    
                    const lines = pdf.splitTextToSize(text, 180)
                    
                    for (let i = 0; i < lines.length; i++) {
                      // Check if we need a new page
                      if (yPos > maxY - 15) {
                        pdf.addPage()
                        yPos = 30
                      }
                      
                      pdf.text(lines[i], margin, yPos)
                      yPos += fontSize * 0.25 + 2 // Reduced spacing by half
                    }
                  }
                  
                  // Add spacing
                  const addSpacing = (space: number = 10) => {
                    yPos += space
                    if (yPos > maxY - 20) {
                      pdf.addPage()
                      yPos = 30
                    }
                  }
                  
                  // Header
                  addTextWithBreaks('Website Analysis Report', 20, true)
                  addSpacing(15)
                  
                  addTextWithBreaks(`URL: ${data.url}`, 12)
                  addTextWithBreaks(`Generated: ${new Date().toLocaleDateString()}`, 12)
                  addSpacing(20)
                  
                  // Main content
                  if (analysisText) {
                    addTextWithBreaks(analysisText, 10)
                  }
                  
                  // Add page numbers
                  const pageCount = (pdf as any).internal.getNumberOfPages()
                  
                  for (let i = 1; i <= pageCount; i++) {
                    pdf.setPage(i)
                    pdf.setFontSize(10)
                    pdf.text(`Page ${i} of ${pageCount}`, pdf.internal.pageSize.width - 40, pdf.internal.pageSize.height - 10)
                  }
                  
                  pdf.save(`website-analysis-${new Date().toISOString().split('T')[0]}.pdf`)
                } catch (error) {
                  console.error('Failed to generate PDF:', error)
                }
              }}
              className="px-3 py-2 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20 text-sm flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              PDF
            </button>
            
            <button
              onClick={onReset}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all duration-200 border border-white/20 text-sm"
            >
              Run Another Reflection
            </button>
          </div>
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
