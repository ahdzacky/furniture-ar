/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './templates/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      colors: {
        primary: '#3498db',
        'primary-container': '#2980b9',
        secondary: '#1a3c47',
        accent: '#3498db',
        surface: {
          DEFAULT: '#f2fbff',
          dim: '#bde0ed',
          bright: '#f2fbff',
          container: {
            lowest: '#ffffff',
            low: '#e4f7ff',
            DEFAULT: '#d5f3ff',
            high: '#cbeefc',
            highest: '#c5e8f6',
          },
        },
        'on-surface': '#001f28',
        'on-surface-variant': '#3f4850',
        'on-primary': '#ffffff',
        outline: '#707881',
        'outline-variant': '#bfc7d2',
        tertiary: '#006497',
        'tertiary-fixed': '#cce5ff',
        'on-tertiary-fixed': '#001e31',
        'secondary-container': '#c5e8f6',
        error: '#ba1a1a',
      },
      screens: {
        '2xl': '1536px',
      },
      boxShadow: {
        'ambient': '0 10px 40px rgba(0,31,40,0.06)',
        'ambient-lg': '0 16px 56px rgba(0,31,40,0.08)',
        'ambient-xl': '0 24px 64px rgba(0,31,40,0.10)',
        'glass': '0 8px 32px rgba(0,31,40,0.12)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      backdropBlur: {
        'glass': '12px',
      },
    },
  },
  plugins: [],
}
