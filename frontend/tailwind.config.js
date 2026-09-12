/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0b0d',
        surface: '#101216',
        surface2: '#15171c',
        border: '#23262d',
        borderStrong: '#33363f',
        text: '#e7e9ec',
        textSecondary: '#9aa1ac',
        textMuted: '#656b76',
        accent: '#8C56D4',
        cyan: '#7DD3FC',
        violet: '#B58AE8',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '10px',
        lg: '14px',
      },
    },
  },
  plugins: [],
}
