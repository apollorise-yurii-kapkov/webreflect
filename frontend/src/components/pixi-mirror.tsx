'use client'

import React, { useEffect, useRef, useState, useCallback } from 'react'
import * as PIXI from 'pixi.js'
import { motion } from 'framer-motion'
import { generateDisplacementMap, generateSilhouetteShape, generateBackgroundTexture } from '@/lib/displacement-generator'

interface PixiMirrorProps {
  width?: number
  height?: number
  onReady?: () => void
  children?: React.ReactNode
}

export function PixiMirror({ width = 1200, height = 700, onReady, children }: PixiMirrorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const appRef = useRef<PIXI.Application | null>(null)
  const [isReady, setIsReady] = useState(false)
  
  const initPixi = useCallback(async () => {
    if (!canvasRef.current || appRef.current) return

    // Create PIXI Application
    let app: PIXI.Application
    try {
      app = new PIXI.Application({
        view: canvasRef.current,
        width,
        height,
        backgroundAlpha: 0,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
      })
      
      if (!app || !app.ticker) {
        console.error('Failed to create PIXI Application')
        return
      }
      
      appRef.current = app
    } catch (error) {
      console.error('Error creating PIXI Application:', error)
      return
    }

    // Generate textures
    const bgCanvas = generateBackgroundTexture(width, height)
    const displacementCanvas = generateDisplacementMap(512, 512)
    const silhouette1Canvas = generateSilhouetteShape(180, 350)
    const silhouette2Canvas = generateSilhouetteShape(160, 320)
    const silhouette3Canvas = generateSilhouetteShape(140, 280)

    // Create textures from canvases
    const bgTexture = PIXI.Texture.from(bgCanvas)
    const displacementTexture = PIXI.Texture.from(displacementCanvas)
    const silhouette1Texture = PIXI.Texture.from(silhouette1Canvas)
    const silhouette2Texture = PIXI.Texture.from(silhouette2Canvas)
    const silhouette3Texture = PIXI.Texture.from(silhouette3Canvas)

    // Background layer (heavily blurred with basic filter)
    const bgSprite = new PIXI.Sprite(bgTexture)
    bgSprite.width = width
    bgSprite.height = height
    
    // Simple blur filter
    const bgBlurFilter = new PIXI.BlurFilter(25)
    bgSprite.filters = [bgBlurFilter]
    
    app.stage.addChild(bgSprite)

    // Mirror dimensions and position
    const mirrorWidth = 900
    const mirrorHeight = 500
    const mirrorX = (width - mirrorWidth) / 2
    const mirrorY = (height - mirrorHeight) / 2
    const mirrorRadius = 36

    // Create mirror mask
    const mirrorMask = new PIXI.Graphics()
    mirrorMask.beginFill(0xffffff)
    mirrorMask.drawRoundedRect(mirrorX, mirrorY, mirrorWidth, mirrorHeight, mirrorRadius)
    mirrorMask.endFill()

    // Mirror container
    const mirrorContainer = new PIXI.Container()
    mirrorContainer.mask = mirrorMask
    app.stage.addChild(mirrorContainer)

    // Background for mirror (same as main bg but will be displaced)
    const mirrorBg = new PIXI.Sprite(bgTexture)
    mirrorBg.width = width
    mirrorBg.height = height
    mirrorContainer.addChild(mirrorBg)

    // Silhouettes behind glass
    const silhouettes = [
      { sprite: new PIXI.Sprite(silhouette1Texture), x: mirrorX + 150, y: mirrorY + 80, scale: 1.2, speed: 0.0008 },
      { sprite: new PIXI.Sprite(silhouette2Texture), x: mirrorX + 450, y: mirrorY + 120, scale: 1.0, speed: 0.0012 },
      { sprite: new PIXI.Sprite(silhouette3Texture), x: mirrorX + 680, y: mirrorY + 90, scale: 0.9, speed: 0.0006 }
    ]

    silhouettes.forEach(({ sprite, x, y, scale }) => {
      sprite.x = x
      sprite.y = y
      sprite.scale.set(scale)
      sprite.alpha = 0.12
      
      // Simple blur for silhouettes
      const silhouetteBlur = new PIXI.BlurFilter(12)
      sprite.filters = [silhouetteBlur]
      
      mirrorContainer.addChild(sprite)
    })

    // Displacement filter for glass effect
    const displacementSprite = new PIXI.Sprite(displacementTexture)
    displacementSprite.x = mirrorX - 100
    displacementSprite.y = mirrorY - 100
    displacementSprite.scale.set(1.5)
    
    const displacementFilter = new PIXI.DisplacementFilter(displacementSprite)
    displacementFilter.scale.x = 20
    displacementFilter.scale.y = 20
    
    mirrorContainer.filters = [displacementFilter]
    
    // Add displacement sprite (invisible but needed for filter)
    app.stage.addChild(displacementSprite)
    displacementSprite.visible = false

    // Animation loop
    let time = 0
    const animate = () => {
      time += 0.016 // ~60fps

      // Animate displacement for breathing glass effect
      displacementSprite.x = mirrorX - 100 + Math.sin(time * 0.8) * 15
      displacementSprite.y = mirrorY - 100 + Math.cos(time * 0.6) * 12
      displacementSprite.rotation = Math.sin(time * 0.3) * 0.1

      // Animate silhouettes
      silhouettes.forEach(({ sprite, speed }, index) => {
        const baseX = mirrorX + 150 + index * 250
        const baseY = mirrorY + 80 + index * 20
        
        sprite.x = baseX + Math.sin(time * speed + index) * 25
        sprite.y = baseY + Math.cos(time * speed * 0.7 + index) * 15
        sprite.scale.set(sprite.scale.x + Math.sin(time * speed * 2 + index) * 0.05)
        sprite.alpha = 0.08 + Math.sin(time * speed * 1.5 + index) * 0.04
      })
    }

    if (app.ticker) {
      app.ticker.add(animate)
    }

    setIsReady(true)
    onReady?.()

    return () => {
      try {
        if (app) {
          app.destroy(true, true)
        }
      } catch (error) {
        console.warn('PIXI app already destroyed:', error)
      }
    }
  }, [width, height, onReady])

  useEffect(() => {
    initPixi()

    return () => {
      try {
        if (appRef.current) {
          appRef.current.destroy(true, true)
          appRef.current = null
        }
      } catch (error) {
        console.warn('PIXI app cleanup error:', error)
      }
    }
  }, [initPixi])

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* PIXI Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ width, height }}
      />
      
      {/* CSS Highlight overlay */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          left: `${(1200 - 900) / 2}px`,
          top: `${(700 - 500) / 2}px`,
          width: '900px',
          height: '500px',
          borderRadius: '36px',
          overflow: 'hidden'
        }}
      >
        <motion.div
          className="absolute w-full h-full"
          style={{
            background: 'linear-gradient(75deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 48%, rgba(255,255,255,0) 100%)',
            transform: 'rotate(8deg) scale(1.5)',
            filter: 'blur(12px)',
            mixBlendMode: 'screen'
          }}
          animate={{
            x: ['-120%', '120%']
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'linear'
          }}
        />
      </div>

      {/* Content overlay */}
      {isReady && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="pointer-events-auto">
            {children}
          </div>
        </div>
      )}
    </div>
  )
}
