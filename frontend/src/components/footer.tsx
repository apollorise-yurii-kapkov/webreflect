'use client'

import { motion } from 'framer-motion'
import { Linkedin, Twitter, Heart, ExternalLink } from 'lucide-react'

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.8 }}
      className="relative z-10 mt-20 py-12 bg-black/20 backdrop-blur-sm border-t border-white/10"
    >
      <div className="container mx-auto px-4">
        <div className="text-center space-y-6">
          {/* Social Links */}
          <div className="flex items-center justify-center gap-6">
            <a
              href="https://www.linkedin.com/company/apollorise"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-blue-400 transition-colors"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-5 h-5" />
            </a>
            <a
              href="https://x.com/ApolloRiseTech"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-blue-400 transition-colors"
              aria-label="X"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
            </a>
          </div>

          {/* Made with love */}
          <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-400 animate-pulse" />
            <span>by the</span>
            <a
              href="https://apollorise.tech"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white font-semibold hover:text-blue-400 transition-colors flex items-center gap-1"
            >
              ApolloRise
              <ExternalLink className="w-3 h-3" />
            </a>
            <span>team</span>
          </div>
        </div>
      </div>
    </motion.footer>
  )
}
