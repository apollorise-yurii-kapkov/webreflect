'use client'

import { motion } from 'framer-motion'
import { Sparkles, Circle } from 'lucide-react'

export function MirrorHero() {
  return (
    <div className="text-center space-y-8 py-12">
      {/* Mirror Visual Element */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative mx-auto w-64 h-64 mb-8"
      >
        {/* Mirror Frame */}
        <div className="mirror-frame w-full h-full">
          {/* Mirror Surface */}
          <div className="mirror-surface">
            {/* Animated Glow */}
            <motion.div
              animate={{ 
                opacity: [0.3, 0.7, 0.3],
                scale: [1, 1.05, 1] 
              }}
              transition={{ 
                duration: 3, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
              className="absolute inset-0 rounded-full bg-gradient-radial from-primary/20 via-transparent to-transparent"
            />
            
            {/* Mirror Icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <Circle className="w-16 h-16 text-primary/60" />
            </div>
          </div>
        </div>
        
        {/* Floating Sparkles */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute"
            style={{
              left: `${20 + (i * 12)}%`,
              top: `${15 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [-5, 5, -5],
              opacity: [0.4, 1, 0.4],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 2 + i * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            }}
          >
            <Sparkles className="w-4 h-4 text-primary/40" />
          </motion.div>
        ))}
      </motion.div>

      {/* Hero Text */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="space-y-6"
      >
        <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight">
          <span className="text-gradient glow-text">
            Website
          </span>
          <br />
          <span className="text-foreground">
            Reflection
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Look into the mirror of your website.{' '}
          <span className="text-primary font-medium">
            See what visitors actually hear.
          </span>
        </p>
      </motion.div>

      {/* Value Proposition */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto pt-8"
      >
        {[
          {
            icon: "🔍",
            title: "Quick Analysis",
            description: "Get honest feedback on your messaging in minutes"
          },
          {
            icon: "🆓",
            title: "Free & Simple",
            description: "No signup required, just paste your URL and reflect"
          },
          {
            icon: "🤖",
            title: "AI-Powered",
            description: "Built with modern AI and design best practices"
          }
        ].map((feature, index) => (
          <motion.div
            key={index}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
            className="glass-effect rounded-lg p-6 text-center hover:bg-accent/5 transition-colors"
          >
            <div className="text-3xl mb-3">{feature.icon}</div>
            <h3 className="font-semibold text-foreground mb-2">
              {feature.title}
            </h3>
            <p className="text-sm text-muted-foreground">
              {feature.description}
            </p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
