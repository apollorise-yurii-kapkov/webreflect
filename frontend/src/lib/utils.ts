import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatUrl(url: string): string {
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`
  }
  return url
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(formatUrl(url))
    return true
  } catch {
    return false
  }
}

export function getProgressMessage(progress: number): string {
  if (progress < 20) return "Initializing analysis..."
  if (progress < 40) return "Crawling website pages..."
  if (progress < 60) return "Extracting content..."
  if (progress < 80) return "Analyzing messaging..."
  if (progress < 100) return "Generating insights..."
  return "Analysis complete!"
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-500"
  if (score >= 60) return "text-yellow-500"
  if (score >= 40) return "text-orange-500"
  return "text-red-500"
}

export function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent"
  if (score >= 80) return "Very Good"
  if (score >= 70) return "Good"
  if (score >= 60) return "Fair"
  if (score >= 50) return "Needs Improvement"
  return "Poor"
}
