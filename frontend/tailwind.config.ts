import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        secondary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      borderColor: {
        border: 'hsl(var(--border))',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'progress': 'progress 2s cubic-bezier(0.4, 0, 0.2, 1) infinite',
        'pulse-bg': 'pulseBackground 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        progress: {
          '0%': { 
            width: '0%', 
            boxShadow: '0 0 5px rgba(14, 165, 233, 0.5)',
            backgroundColor: '#38bdf8'
          },
          '30%': { 
            width: '50%',
            backgroundColor: '#0ea5e9'
          },
          '60%': { 
            width: '85%',
            backgroundColor: '#0284c7'
          },
          '100%': { 
            width: '100%',
            boxShadow: '0 0 10px rgba(14, 165, 233, 0.8)',
            backgroundColor: '#38bdf8'
          },
        },
        pulseBackground: {
          '0%, 100%': { backgroundColor: 'rgba(14, 165, 233, 0.7)' },
          '50%': { backgroundColor: 'rgba(14, 165, 233, 0.9)' },
        },
      },
    },
  },
  plugins: [],
}
export default config
