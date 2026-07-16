/** Iron Ridge Module 1 design tokens (non-CSS usage). */
export const colors = {
  charcoal: "#1F2937",
  background: "#F8FAFC",
  white: "#FFFFFF",
  accentRed: "#C62828",
  accentOrange: "#F97316",
  steelGray: "#6B7280",
  success: "#15803D",
} as const;

export const spacing = {
  xs: "0.25rem",
  sm: "0.5rem",
  md: "1rem",
  lg: "1.5rem",
  xl: "2rem",
  "2xl": "3rem",
  "3xl": "4rem",
} as const;

export const radius = {
  sm: "0.375rem",
  md: "0.5rem",
  lg: "0.625rem",
  xl: "0.75rem",
  full: "9999px",
} as const;

export const typography = {
  display: { size: "3.75rem", weight: "700", lineHeight: "1.1" },
  heading: { size: "2.25rem", weight: "700", lineHeight: "1.2" },
  subheading: { size: "1.25rem", weight: "500", lineHeight: "1.5" },
  body: { size: "1rem", weight: "400", lineHeight: "1.6" },
  caption: { size: "0.875rem", weight: "400", lineHeight: "1.4" },
} as const;
