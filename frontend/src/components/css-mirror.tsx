'use client'

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface CSSMirrorProps {
  children?: React.ReactNode
}

interface Particle {
  id: number
  left: number
  top: number
  animateX: number
  animateY: number
  duration: number
  delay: number
}

export function CSSMirror({ children }: CSSMirrorProps) {
  const [particles, setParticles] = useState<Particle[]>([])

  useEffect(() => {
    // Generate particles on client-side to avoid hydration mismatch
    const newParticles = [...Array(30)].map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      animateX: Math.random() * 200 - 100,
      animateY: Math.random() * 200 - 100,
      duration: Math.random() * 6 + 4,
      delay: Math.random() * 3,
    }))
    setParticles(newParticles)
  }, [])

  return (
    <div className="relative w-full h-full bg-black flex items-center justify-center overflow-hidden">
      {/* Enhanced animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-800">
        {/* Floating particles with more variety */}
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute rounded-full"
            animate={{
              x: [0, particle.animateX],
              y: [0, particle.animateY],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
              width: `${2 + (particle.id % 3)}px`,
              height: `${2 + (particle.id % 3)}px`,
              background: `radial-gradient(circle, ${['rgba(59, 130, 246, 0.6)', 'rgba(147, 51, 234, 0.6)', 'rgba(236, 72, 153, 0.6)'][particle.id % 3]}, transparent)`,
            }}
          />
        ))}
      </div>

      {/* Enhanced mirror container */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0, rotateX: 15 }}
          animate={{ scale: 1, opacity: 1, rotateX: 0 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="relative"
          style={{ perspective: '1000px' }}
        >
          {/* Mirror frame with enhanced effects */}
          <div className="relative bg-gradient-to-br from-gray-700/20 to-gray-900/40 backdrop-blur-2xl border-2 border-white/20 rounded-2xl sm:rounded-[2.5rem] p-6 sm:p-12 md:p-20 shadow-[0_0_80px_rgba(59,130,246,0.3)] overflow-hidden">
            
            {/* Mirror surface with realistic reflections */}
            <div className="absolute inset-2 sm:inset-4 rounded-xl sm:rounded-[2rem] overflow-hidden bg-gradient-to-br from-gray-800/60 to-gray-900/80 backdrop-blur-3xl">
              
              {/* Animated silhouettes behind glass - more prominent */}
              {[0, 1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  className="absolute bg-black/25 rounded-full blur-xl"
                  style={{
                    width: `${150 + i * 30}px`,
                    height: `${400 + i * 50}px`,
                    left: `${15 + i * 20}%`,
                    top: `${5 + i * 8}%`,
                  }}
                  animate={{
                    x: [0, [25, -15, 20, -10][i], 0],
                    y: [0, [20, 15, -18, 12][i], 0],
                    scale: [1, 1.1, 1],
                    opacity: [0.15, 0.3, 0.15],
                  }}
                  transition={{
                    duration: 8 + i * 2,
                    repeat: Infinity,
                    delay: i * 1.2,
                  }}
                />
              ))}

              {/* Enhanced color shifting background */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 blur-3xl"
                animate={{
                  background: [
                    'linear-gradient(45deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2), rgba(236, 72, 153, 0.2))',
                    'linear-gradient(45deg, rgba(147, 51, 234, 0.2), rgba(236, 72, 153, 0.2), rgba(34, 197, 94, 0.2))',
                    'linear-gradient(45deg, rgba(236, 72, 153, 0.2), rgba(34, 197, 94, 0.2), rgba(59, 130, 246, 0.2))',
                  ]
                }}
                transition={{ duration: 12, repeat: Infinity }}
              />
            </div>

            {/* Multiple glass distortion layers */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/8 to-transparent"
              animate={{
                x: ['-150%', '250%'],
                skewX: [0, 8, 0],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: 'linear',
              }}
              style={{ filter: 'blur(1px)' }}
            />

            <motion.div
              className="absolute inset-0 bg-gradient-to-l from-transparent via-white/6 to-transparent"
              animate={{
                x: ['200%', '-150%'],
                skewX: [0, -5, 0],
              }}
              transition={{
                duration: 7,
                repeat: Infinity,
                ease: 'linear',
                delay: 2,
              }}
              style={{ filter: 'blur(2px)' }}
            />

            {/* Enhanced shimmer highlights */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/15 to-transparent"
              animate={{
                x: ['-200%', '200%'],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: 'linear',
              }}
              style={{
                transform: 'rotate(12deg) scale(2)',
                filter: 'blur(12px)',
                mixBlendMode: 'screen',
              }}
            />

            {/* Corner light reflections */}
            <div className="absolute top-4 right-4 w-32 h-32 bg-gradient-to-br from-white/20 to-transparent rounded-full blur-2xl" />
            <div className="absolute bottom-4 left-4 w-24 h-24 bg-gradient-to-tr from-blue-400/20 to-transparent rounded-full blur-xl" />

            {/* Enhanced noise texture */}
            <div 
              className="absolute inset-0 opacity-20 mix-blend-mode-overlay"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.2' numOctaves='6' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              }}
            />

            {/* Content with enhanced positioning */}
            <div className="relative z-20 flex items-center justify-center min-h-[65dvh] sm:min-h-[520px]">
              {children}
            </div>
          </div>

          {/* Mirror reflection on floor */}
          <motion.div
            className="absolute top-full left-0 right-0 h-32 bg-gradient-to-b from-gray-800/10 to-transparent"
            style={{
              transform: 'scaleY(-0.3) translateY(-100%)',
              filter: 'blur(8px)',
              maskImage: 'linear-gradient(to bottom, rgba(0,0,0,0.3), transparent)',
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 1 }}
          />
        </motion.div>
      </div>
    </div>
  )
}
