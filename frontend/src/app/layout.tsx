import React from 'react'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Script from 'next/script'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Website Reflection - See Your Website\'s True Reflection | Free AI Analysis',
  description: 'Paste your URL and watch AI uncover the real message your site delivers. Get a free website content & messaging audit with actionable insights in one clear, objective summary. Discover what your website really communicates to visitors.',
  keywords: 'website analysis, messaging analysis, AI website audit, free website review, content analysis, marketing messaging, website reflection, site audit tool, website messaging, digital marketing analysis, SEO audit, website optimization',
  authors: [{ name: 'ApolloRise', url: 'https://apollorise.tech' }],
  creator: 'ApolloRise',
  publisher: 'ApolloRise',
  robots: 'index, follow',
  metadataBase: new URL('https://reflection.apollorise.tech'),
  openGraph: {
    title: 'Website Reflection - See Your Website\'s True Reflection',
    description: 'Free AI-powered website messaging analysis. Discover what your site really communicates to visitors. Get actionable insights and improve your website\'s messaging in minutes.',
    url: 'https://reflection.apollorise.tech',
    siteName: 'Website Reflection',
    images: [
      {
        url: '/images/og_reflection.png',
        width: 1200,
        height: 630,
        alt: 'Website Reflection - AI Website Analysis Tool | See Your Website\'s True Reflection',
        type: 'image/png',
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
    site: '@ApolloRiseTech',
    images: ['/images/og_reflection.png'],
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
  maximumScale: 1,
  userScalable: false,
  themeColor: '#000000',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className="bg-black">
      <body 
        className={`${inter.className} bg-black`}
        suppressHydrationWarning={true}
        style={{ backgroundColor: '#000000' }}
      >
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-KJ6ZN6MHEV"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-KJ6ZN6MHEV');
          `}
        </Script>
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
