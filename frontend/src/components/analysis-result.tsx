'use client'

import { motion } from 'framer-motion'
import { Share2, Download, RotateCcw, CheckCircle, TrendingUp, Users, MessageSquare, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { getScoreColor, getScoreLabel } from '@/lib/utils'
import { AnalysisData } from '@/app/page'

interface AnalysisResultProps {
  data: AnalysisData
  onReset: () => void
}

export function AnalysisResult({ data, onReset }: AnalysisResultProps) {
  const result = data.result
  const scores = result?.scores
  const analysis = result?.messaging_analysis
  const quickWins = result?.quick_wins || []

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
                  {analysis.strengths.map((strength, index) => (
                    <li key={index} className="text-muted-foreground text-sm flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-orange-500 mb-2">Areas for Improvement</h3>
                <ul className="space-y-1">
                  {analysis.weaknesses.map((weakness, index) => (
                    <li key={index} className="text-muted-foreground text-sm flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      {weakness}
                    </li>
                  ))}
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
            {quickWins.map((win, index) => (
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
          onClick={() => {
            navigator.share?.({
              title: 'Website Reflection Analysis',
              text: `Check out my website analysis results!`,
              url: window.location.href,
            }) || navigator.clipboard.writeText(window.location.href)
          }}
          className="glass-effect"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Share Results
        </Button>
        
        <Button
          variant="outline"
          size="lg"
          onClick={() => {
            // TODO: Implement PDF generation
            console.log('Generate PDF')
          }}
          className="glass-effect"
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
