import React from 'react'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Website Reflection - See Your Website\'s True Reflection | Free AI Analysis',
  description: 'Paste your URL and watch AI uncover the real message your site delivers. A free website content & messaging audit — in one clear, objective summary.',
  keywords: 'website analysis, messaging analysis, AI website audit, free website review, content analysis, marketing messaging, website reflection, site audit tool, website messaging, digital marketing analysis',
  authors: [{ name: 'ApolloRise', url: 'https://apollorise.tech' }],
  creator: 'ApolloRise',
  publisher: 'ApolloRise',
  robots: 'index, follow',
  openGraph: {
    title: 'Website Reflection - See Your Website\'s True Reflection',
    description: 'Free AI-powered website messaging analysis. Discover what your site really communicates to visitors.',
    url: 'https://reflection.apollorise.tech',
    siteName: 'Website Reflection',
    images: [
      {
        url: '/images/favicon.png',
        width: 1200,
        height: 630,
        alt: 'Website Reflection - AI Website Analysis Tool',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Website Reflection - See Your Website\'s True Reflection',
    description: 'Free AI-powered website messaging analysis. Discover what your site really communicates to visitors.',
    creator: '@ApolloRiseTech',
    images: ['/images/favicon.png'],
  },
  icons: {
    icon: [
      { url: '/images/favicon.ico' },
      { url: '/images/favicon.png', type: 'image/png' },
    ],
    apple: [
      { url: '/images/apple-touch-icon-76x76.png', sizes: '76x76' },
      { url: '/images/apple-touch-icon-120x120.png', sizes: '120x120' },
      { url: '/images/apple-touch-icon-152x152.png', sizes: '152x152' },
      { url: '/images/apple-touch-icon-180x180.png', sizes: '180x180' },
    ],
  },
  manifest: '/manifest.json',
  category: 'technology',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body 
        className={inter.className}
        suppressHydrationWarning={true}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
