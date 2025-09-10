'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Globe, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { analysisApi } from '@/lib/api'
import { formatUrl, isValidUrl } from '@/lib/utils'
import { AnalysisData } from '@/app/page'

interface AnalysisFormProps {
  onAnalysisStart: (data: AnalysisData) => void
}

export function AnalysisForm({ onAnalysisStart }: AnalysisFormProps) {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a website URL')
      return
    }

    const formattedUrl = formatUrl(url.trim())
    
    if (!isValidUrl(formattedUrl)) {
      setError('Please enter a valid website URL')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const response = await analysisApi.startAnalysis({ url: formattedUrl })
      
      onAnalysisStart({
        jobId: response.job_id,
        url: response.url,
        status: response.status,
        progress: 0
      })

      toast({
        title: "Analysis Started",
        description: "Your website is being analyzed. This may take a few minutes.",
      })

    } catch (error: any) {
      console.error('Analysis start error:', error)
      
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to start analysis. Please try again.'
      
      setError(errorMessage)
      
      toast({
        title: "Analysis Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* How it Works */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="mb-12"
      >
        <h2 className="text-2xl font-semibold text-center mb-8">
          How it works
        </h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              step: "1",
              icon: <Search className="w-6 h-6" />,
              title: "Crawl",
              description: "We scan your pages"
            },
            {
              step: "2", 
              icon: <Globe className="w-6 h-6" />,
              title: "Reflect",
              description: "AI condenses your core message"
            },
            {
              step: "3",
              icon: <AlertCircle className="w-6 h-6" />,
              title: "Reveal",
              description: "You get a one-page reflection"
            }
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
              className="text-center space-y-3"
            >
              <div className="w-16 h-16 mx-auto mirror-frame flex items-center justify-center text-primary">
                {item.icon}
              </div>
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-sm text-muted-foreground">{item.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Analysis Form */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="glass-effect rounded-2xl p-8"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="url" className="text-sm font-medium text-foreground">
              Paste your website link here
            </label>
            <div className="relative">
              <Input
                id="url"
                type="url"
                placeholder="https://yourwebsite.com"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value)
                  setError('')
                }}
                className="h-12 text-lg glass-effect border-border/20 focus:border-primary/50"
                disabled={isLoading}
              />
              <Globe className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            </div>
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-destructive flex items-center gap-2"
              >
                <AlertCircle className="w-4 h-4" />
                {error}
              </motion.p>
            )}
          </div>

          <Button
            type="submit"
            size="lg"
            disabled={isLoading || !url.trim()}
            className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg hover:shadow-xl transition-all duration-200"
          >
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-6 h-6 border-2 border-primary-foreground border-t-transparent rounded-full"
              />
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                Reflect My Site
              </>
            )}
          </Button>
        </form>

        {/* Sample Preview */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-8 pt-6 border-t border-border/20"
        >
          <p className="text-sm text-muted-foreground text-center mb-4">
            Sample output preview
          </p>
          
          <div className="glass-effect rounded-lg p-4 space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="font-medium">Overall Score</span>
              <span className="text-primary font-bold">78/100</span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Clarity</span>
                <span>85</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Consistency</span>
                <span>72</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">CTA Strength</span>
                <span>81</span>
              </div>
            </div>
            <div className="pt-2 border-t border-border/10">
              <p className="text-xs text-muted-foreground">
                <strong>Quick Win:</strong> Add customer testimonials to build trust
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}
