/**
 * Generates displacement map textures for glass refraction effects
 */

export function generateDisplacementMap(width: number = 512, height: number = 512): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  
  const ctx = canvas.getContext('2d')!
  const imageData = ctx.createImageData(width, height)
  const data = imageData.data
  
  // Generate Perlin-like noise for smooth displacement
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = (y * width + x) * 4
      
      // Create smooth noise pattern
      const noise1 = Math.sin(x * 0.01) * Math.cos(y * 0.01)
      const noise2 = Math.sin(x * 0.02 + Math.PI/3) * Math.cos(y * 0.02 + Math.PI/3)
      const noise3 = Math.sin(x * 0.005) * Math.cos(y * 0.005)
      
      const combined = (noise1 + noise2 * 0.5 + noise3 * 0.3) / 1.8
      const normalized = (combined + 1) * 0.5 // Normalize to 0-1
      
      const value = Math.floor(normalized * 255)
      
      data[index] = value     // R
      data[index + 1] = value // G
      data[index + 2] = value // B
      data[index + 3] = 255   // A
    }
  }
  
  ctx.putImageData(imageData, 0, 0)
  return canvas
}

export function generateSilhouetteShape(width: number = 200, height: number = 400): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  
  const ctx = canvas.getContext('2d')!
  
  // Create organic blob-like silhouette
  ctx.fillStyle = 'rgba(0, 0, 0, 0.15)'
  ctx.beginPath()
  
  const centerX = width / 2
  const centerY = height / 2
  const baseRadius = Math.min(width, height) * 0.3
  
  // Generate organic shape using multiple sine waves
  const points = 32
  for (let i = 0; i <= points; i++) {
    const angle = (i / points) * Math.PI * 2
    
    // Add multiple frequency variations for organic look
    const variation1 = Math.sin(angle * 3) * 0.3
    const variation2 = Math.sin(angle * 5) * 0.15
    const variation3 = Math.sin(angle * 7) * 0.1
    
    const radius = baseRadius * (1 + variation1 + variation2 + variation3)
    
    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius * 1.8 // Make it taller
    
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  }
  
  ctx.closePath()
  ctx.fill()
  
  // Add some blur effect
  ctx.filter = 'blur(8px)'
  ctx.globalCompositeOperation = 'source-over'
  ctx.drawImage(canvas, 0, 0)
  
  return canvas
}

export function generateBackgroundTexture(width: number = 1200, height: number = 800): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  
  const ctx = canvas.getContext('2d')!
  
  // Create abstract background with gradients
  const gradient1 = ctx.createRadialGradient(width * 0.3, height * 0.3, 0, width * 0.3, height * 0.3, width * 0.8)
  gradient1.addColorStop(0, 'rgba(59, 130, 246, 0.4)')
  gradient1.addColorStop(0.5, 'rgba(147, 51, 234, 0.3)')
  gradient1.addColorStop(1, 'rgba(0, 0, 0, 0.8)')
  
  const gradient2 = ctx.createRadialGradient(width * 0.7, height * 0.7, 0, width * 0.7, height * 0.7, width * 0.6)
  gradient2.addColorStop(0, 'rgba(236, 72, 153, 0.3)')
  gradient2.addColorStop(0.5, 'rgba(59, 130, 246, 0.2)')
  gradient2.addColorStop(1, 'rgba(0, 0, 0, 0.6)')
  
  ctx.fillStyle = gradient1
  ctx.fillRect(0, 0, width, height)
  
  ctx.globalCompositeOperation = 'screen'
  ctx.fillStyle = gradient2
  ctx.fillRect(0, 0, width, height)
  
  // Add some noise texture
  ctx.globalCompositeOperation = 'overlay'
  for (let i = 0; i < 2000; i++) {
    const x = Math.random() * width
    const y = Math.random() * height
    const opacity = Math.random() * 0.1
    
    ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`
    ctx.fillRect(x, y, 1, 1)
  }
  
  return canvas
}
