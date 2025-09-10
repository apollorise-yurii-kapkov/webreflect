'use client'

import { motion } from 'framer-motion'
import { Share2, Download, RotateCcw, CheckCircle, TrendingUp, Users, MessageSquare, Zap, Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { getScoreColor, getScoreLabel } from '@/lib/utils'
import { AnalysisData } from '@/app/page'
import { useToast } from '@/components/ui/use-toast'
import { analysisApi } from '@/lib/api'
import jsPDF from 'jspdf'

interface AnalysisResultProps {
  data: AnalysisData
  onReset: () => void
}

export function AnalysisResult({ data, onReset }: AnalysisResultProps) {
  const { toast } = useToast()
  const result = data.result
  const scores = result?.scores
  const analysis = result?.messaging_analysis
  const quickWins = result?.quick_wins || []

  const copyToClipboard = async () => {
    const reportText = generateReportText()
    try {
      await navigator.clipboard.writeText(reportText)
      toast({
        title: "Copied to clipboard",
        description: "Analysis report has been copied to your clipboard.",
      })
    } catch (err) {
      toast({
        title: "Copy failed",
        description: "Unable to copy to clipboard. Please try again.",
        variant: "destructive",
      })
    }
  }

  const shareReport = async () => {
    try {
      // First, mark the report as shared on the backend
      await analysisApi.shareReport(data.jobId)
      
      // Create share URL with just 'id' parameter
      const shareUrl = `${window.location.origin}?id=${data.jobId}`
      
      if (navigator.share) {
        try {
          await navigator.share({
            title: 'Website Reflection Analysis',
            text: `Check out my website analysis results for ${data.url}!`,
            url: shareUrl,
          })
        } catch (err) {
          // User cancelled sharing
        }
      } else {
        // Fallback to copying URL
        try {
          await navigator.clipboard.writeText(shareUrl)
          toast({
            title: "Share link copied",
            description: "Share URL has been copied to your clipboard.",
          })
        } catch (err) {
          toast({
            title: "Share failed",
            description: "Unable to copy share link. Please try again.",
            variant: "destructive",
          })
        }
      }
    } catch (error) {
      toast({
        title: "Share failed",
        description: "Unable to create share link. Please try again.",
        variant: "destructive",
      })
    }
  }

  const generatePDF = () => {
    const pdf = new jsPDF()
    
    // Header
    pdf.setFontSize(20)
    pdf.text('Website Reflection Analysis', 20, 30)
    
    pdf.setFontSize(12)
    pdf.text(`URL: ${data.url}`, 20, 45)
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 55)
    
    let yPos = 75
    
    // Overall Score
    if (scores) {
      pdf.setFontSize(16)
      pdf.text('Overall Score', 20, yPos)
      yPos += 15
      
      pdf.setFontSize(24)
      pdf.text(`${scores.overall}/100`, 20, yPos)
      yPos += 25
    }
    
    // Individual Scores
    if (scores) {
      pdf.setFontSize(16)
      pdf.text('Detailed Scores', 20, yPos)
      yPos += 15
      
      pdf.setFontSize(12)
      const scoreItems = [
        { name: 'Clarity', value: scores.clarity },
        { name: 'Consistency', value: scores.consistency },
        { name: 'Differentiation', value: scores.differentiation },
        { name: 'Social Proof', value: scores.proof },
        { name: 'CTA Strength', value: scores.cta_strength },
        { name: 'Audience Fit', value: scores.audience_fit },
      ]
      
      scoreItems.forEach(item => {
        pdf.text(`${item.name}: ${item.value}/100`, 20, yPos)
        yPos += 10
      })
      yPos += 10
    }
    
    // Content Summary
    if (result?.content_summary) {
      pdf.setFontSize(16)
      pdf.text('Content Summary', 20, yPos)
      yPos += 15
      
      pdf.setFontSize(10)
      const summaryLines = pdf.splitTextToSize(result.content_summary, 170)
      pdf.text(summaryLines, 20, yPos)
      yPos += summaryLines.length * 5 + 15
    }
    
    // Quick Wins
    if (quickWins.length > 0) {
      pdf.setFontSize(16)
      pdf.text('Quick Wins', 20, yPos)
      yPos += 15
      
      pdf.setFontSize(10)
      quickWins.forEach((win: string, index: number) => {
        const winLines = pdf.splitTextToSize(`${index + 1}. ${win}`, 170)
        pdf.text(winLines, 20, yPos)
        yPos += winLines.length * 5 + 5
      })
    }
    
    pdf.save(`website-analysis-${new Date().toISOString().split('T')[0]}.pdf`)
    
    toast({
      title: "PDF Downloaded",
      description: "Your analysis report has been downloaded as PDF.",
    })
  }

  const generateReportText = () => {
    let report = `Website Reflection Analysis\n`
    report += `URL: ${data.url}\n`
    report += `Generated: ${new Date().toLocaleDateString()}\n\n`
    
    if (scores) {
      report += `Overall Score: ${scores.overall}/100\n\n`
      report += `Detailed Scores:\n`
      report += `- Clarity: ${scores.clarity}/100\n`
      report += `- Consistency: ${scores.consistency}/100\n`
      report += `- Differentiation: ${scores.differentiation}/100\n`
      report += `- Social Proof: ${scores.proof}/100\n`
      report += `- CTA Strength: ${scores.cta_strength}/100\n`
      report += `- Audience Fit: ${scores.audience_fit}/100\n\n`
    }
    
    if (result?.content_summary) {
      report += `Content Summary:\n${result.content_summary}\n\n`
    }
    
    if (analysis) {
      report += `Messaging Analysis:\n`
      report += `Primary Message: ${analysis.primary_message}\n`
      report += `Target Audience: ${analysis.target_audience}\n`
      report += `Value Proposition: ${analysis.value_proposition}\n`
      report += `Tone & Voice: ${analysis.tone_and_voice}\n\n`
      
      if (analysis.strengths?.length > 0) {
        report += `Strengths:\n`
        analysis.strengths.forEach((strength: string, index: number) => {
          report += `${index + 1}. ${strength}\n`
        })
        report += `\n`
      }
      
      if (analysis.weaknesses?.length > 0) {
        report += `Areas for Improvement:\n`
        analysis.weaknesses.forEach((weakness: string, index: number) => {
          report += `${index + 1}. ${weakness}\n`
        })
        report += `\n`
      }
    }
    
    if (quickWins.length > 0) {
      report += `Quick Wins:\n`
      quickWins.forEach((win: string, index: number) => {
        report += `${index + 1}. ${win}\n`
      })
    }
    
    return report
  }

  const scoreItems = scores ? [
    { name: 'Clarity', value: scores.clarity, icon: MessageSquare },
    { name: 'Consistency', value: scores.consistency, icon: CheckCircle },
    { name: 'Differentiation', value: scores.differentiation, icon: TrendingUp },
    { name: 'Social Proof', value: scores.proof, icon: Users },
    { name: 'CTA Strength', value: scores.cta_strength, icon: Zap },
    { name: 'Audience Fit', value: scores.audience_fit, icon: Users },
  ] : []

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="w-16 h-16 mx-auto mirror-frame flex items-center justify-center">
          <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold">Website Reflection Complete</h1>
        <p className="text-muted-foreground">
          Analysis for: <span className="text-primary font-medium">{data.url}</span>
        </p>
      </motion.div>

      {/* Overall Score */}
      {scores && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="glass-effect rounded-2xl p-8 text-center"
        >
          <h2 className="text-2xl font-semibold mb-6">Overall Messaging Score</h2>
          <div className="relative w-32 h-32 mx-auto mb-6">
            <div className="mirror-frame w-full h-full">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getScoreColor(scores.overall)}`}>
                    {scores.overall}
                  </div>
                  <p className="text-sm text-muted-foreground">Here&apos;s what we found about your website&apos;s messaging:</p>
                </div>
              </div>
            </div>
          </div>
          <p className={`text-lg font-medium ${getScoreColor(scores.overall)}`}>
            {getScoreLabel(scores.overall)}
          </p>
        </motion.div>
      )}

      {/* Detailed Scores */}
      {scoreItems.length > 0 && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass-effect rounded-2xl p-8"
        >
          <h2 className="text-2xl font-semibold mb-6">Detailed Analysis</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {scoreItems.map((item, index) => (
              <motion.div
                key={item.name}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                className="space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <item.icon className="w-5 h-5 text-primary" />
                    <span className="font-medium">{item.name}</span>
                  </div>
                  <span className={`font-bold ${getScoreColor(item.value)}`}>
                    {item.value}/100
                  </span>
                </div>
                <Progress value={item.value} className="h-2" />
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Messaging Analysis */}
      {analysis && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="glass-effect rounded-2xl p-8"
        >
          <h2 className="text-2xl font-semibold mb-6">Messaging Insights</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-primary mb-2">Primary Message</h3>
                <p className="text-muted-foreground">{analysis.primary_message}</p>
              </div>
              <div>
                <h3 className="font-semibold text-primary mb-2">Target Audience</h3>
                <p className="text-muted-foreground">{analysis.target_audience}</p>
              </div>
              <div>
                <h3 className="font-semibold text-primary mb-2">Value Proposition</h3>
                <p className="text-muted-foreground">{analysis.value_proposition}</p>
              </div>
            </div>
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-green-500 mb-2">Strengths</h3>
                <ul className="space-y-1">
                  {analysis.strengths?.map((strength: string, index: number) => (
                    <li key={index} className="text-muted-foreground text-sm flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  )) || <li className="text-muted-foreground text-sm">No strengths data available</li>}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-orange-500 mb-2">Areas for Improvement</h3>
                <ul className="space-y-1">
                  {analysis.weaknesses?.map((weakness: string, index: number) => (
                    <li key={index} className="text-muted-foreground text-sm flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      {weakness}
                    </li>
                  )) || <li className="text-muted-foreground text-sm">No weaknesses data available</li>}
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Quick Wins */}
      {quickWins.length > 0 && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="glass-effect rounded-2xl p-8"
        >
          <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Zap className="w-6 h-6 text-primary" />
            Quick Wins
          </h2>
          <p className="text-muted-foreground mb-6">
            Easy improvements that could immediately enhance your website&apos;s messaging:
          </p>
          <div className="space-y-4">
            {quickWins.map((win: string, index: number) => (
              <motion.div
                key={index}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                className="flex items-start gap-3 p-4 rounded-lg bg-primary/5 border border-primary/10"
              >
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-primary">{index + 1}</span>
                </div>
                <p className="text-sm">{win}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="flex flex-wrap gap-4 justify-center"
      >
        <Button
          variant="outline"
          size="lg"
          onClick={copyToClipboard}
          className="mirror-button"
        >
          <Copy className="w-4 h-4 mr-2" />
          Copy Report
        </Button>
        
        <Button
          variant="outline"
          size="lg"
          onClick={shareReport}
          className="mirror-button"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Share Results
        </Button>
        
        <Button
          variant="outline"
          size="lg"
          onClick={generatePDF}
        >
          <Download className="w-4 h-4 mr-2" />
          Download PDF
        </Button>
        
        <Button
          variant="mirror"
          size="lg"
          onClick={onReset}
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Analyze Another Site
        </Button>
      </motion.div>
    </div>
  )
}
