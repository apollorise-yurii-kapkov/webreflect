'use client'

import { motion } from 'framer-motion'
import { Github, Twitter, Heart } from 'lucide-react'

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.8 }}
      className="mt-20 py-12 border-t border-border/20"
    >
      <div className="container mx-auto px-4">
        <div className="text-center space-y-6">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2">
            <div className="w-8 h-8 mirror-frame flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-primary/60" />
            </div>
            <span className="text-lg font-display font-semibold">
              Website Reflection
            </span>
          </div>

          {/* Description */}
          <p className="text-muted-foreground max-w-md mx-auto">
            A free tool to analyze your website&apos;s messaging and discover what visitors actually hear.
          </p>

          {/* Links */}
          <div className="flex items-center justify-center gap-6">
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
          </div>

          {/* Copyright */}
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-500" />
            <span>for better websites</span>
          </div>
        </div>
      </div>
    </motion.footer>
  )
}
