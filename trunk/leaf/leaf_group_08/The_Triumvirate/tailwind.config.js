module.exports = {
  content: [
    "./pages/*.{html,js}",
    "./index.html",
    "./components/**/*.{html,js}",
    "./src/**/*.{html,js}"
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Core Manifesto Authority
        primary: {
          DEFAULT: "#1E3A8A", // blue-900
          50: "#EFF6FF", // blue-50
          100: "#DBEAFE", // blue-100
          200: "#BFDBFE", // blue-200
          300: "#93C5FD", // blue-300
          400: "#60A5FA", // blue-400
          500: "#3B82F6", // blue-500
          600: "#2563EB", // blue-600
          700: "#1D4ED8", // blue-700
          800: "#1E40AF", // blue-800
          900: "#1E3A8A", // blue-900
        },
        // Secondary - Technical Precision
        secondary: {
          DEFAULT: "#0891B2", // cyan-600
          50: "#ECFEFF", // cyan-50
          100: "#CFFAFE", // cyan-100
          200: "#A5F3FC", // cyan-200
          300: "#67E8F9", // cyan-300
          400: "#22D3EE", // cyan-400
          500: "#06B6D4", // cyan-500
          600: "#0891B2", // cyan-600
          700: "#0E7490", // cyan-700
          800: "#155E75", // cyan-800
          900: "#164E63", // cyan-900
        },
        // Accent - Breakthrough Emphasis
        accent: {
          DEFAULT: "#06B6D4", // cyan-500
          light: "#22D3EE", // cyan-400
          dark: "#0891B2", // cyan-600
        },
        // Background - Deep Contemplative Canvas
        background: {
          DEFAULT: "#0F172A", // slate-900
          light: "#1E293B", // slate-800
          lighter: "#334155", // slate-700
        },
        // Surface - Content Elevation
        surface: {
          DEFAULT: "#1E293B", // slate-800
          light: "#334155", // slate-700
          lighter: "#475569", // slate-600
        },
        // Text - Reading Clarity
        text: {
          primary: "#F8FAFC", // slate-50
          secondary: "#94A3B8", // slate-400
          tertiary: "#64748B", // slate-500
          muted: "#475569", // slate-600
        },
        // Semantic Colors
        success: {
          DEFAULT: "#10B981", // emerald-500
          light: "#34D399", // emerald-400
          dark: "#059669", // emerald-600
        },
        warning: {
          DEFAULT: "#F59E0B", // amber-500
          light: "#FBBF24", // amber-400
          dark: "#D97706", // amber-600
        },
        error: {
          DEFAULT: "#EF4444", // red-500
          light: "#F87171", // red-400
          dark: "#DC2626", // red-600
        },
      },
      fontFamily: {
        headline: ['JetBrains Mono', 'monospace'],
        body: ['Inter', 'sans-serif'],
        cta: ['Space Grotesk', 'sans-serif'],
        code: ['Fira Code', 'monospace'],
      },
      boxShadow: {
        subtle: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        medium: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        dramatic: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'glow-primary': '0 0 20px rgba(30, 58, 138, 0.5)',
        'glow-secondary': '0 0 20px rgba(8, 145, 178, 0.5)',
        'glow-accent': '0 0 20px rgba(6, 182, 212, 0.5)',
      },
      transitionDuration: {
        fast: '200ms',
        base: '300ms',
        slow: '500ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
        'ease-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      animation: {
        'fade-in': 'fadeIn 300ms cubic-bezier(0, 0, 0.2, 1)',
        'slide-up': 'slideUp 300ms cubic-bezier(0, 0, 0.2, 1)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
}