import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Website Analysis Report | Website Reflection',
  description: 'View your comprehensive website messaging analysis report. Get insights on clarity, consistency, differentiation, and actionable recommendations to improve your website.',
  openGraph: {
    title: 'Website Analysis Report | Website Reflection',
    description: 'View your comprehensive website messaging analysis report with actionable insights.',
    type: 'website',
    images: [
      {
        url: '/images/og_reflection.png',
        width: 1200,
        height: 630,
        alt: 'Website Reflection - Analysis Report',
        type: 'image/png',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Website Analysis Report | Website Reflection',
    description: 'View your comprehensive website messaging analysis report with actionable insights.',
    images: ['/images/og_reflection.png'],
  },
}

export default function ReportLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}


