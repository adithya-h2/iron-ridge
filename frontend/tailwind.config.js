/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: '#12151A',   // hull — main background
          raised: '#1A1E25',    // panel surface
          inset: '#0D0F13',     // recessed surface
        },
        line: {
          DEFAULT: '#262B33',   // hairline borders
          soft: '#1E2229',
        },
        ink: {
          DEFAULT: '#E7EAEE',   // primary text
          muted: '#8B93A1',     // secondary text
          faint: '#565D68',     // disabled / tertiary
        },
        signal: {
          DEFAULT: '#FF9500',   // dispatch amber — primary accent
          dim: '#8A5218',
          bg: '#2A1E0C',
        },
        alarm: {
          DEFAULT: '#EF4444',   // code-red — rejections, overdue
          bg: '#2A1414',
        },
        clear: {
          DEFAULT: '#2DD4A7',   // clear-to-proceed green
          bg: '#0E2620',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.03) inset',
      },
    },
  },
  plugins: [],
}
