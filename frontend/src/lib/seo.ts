import type { Metadata } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const siteConfig = {
  name: "Iron Ridge",
  tagline: "Emergency Vehicles. Built Faster. Delivered Smarter.",
  description:
    "Iron Ridge manufactures emergency response vehicles for fire departments, EMS, hospitals, and municipal governments across the United States.",
  url: siteUrl,
  ogImage: "/images/og-default.jpg",
  contact: {
    phone: "+1 (800) 555-0199",
    email: "sales@ironridgevehicles.com",
    address: "1200 Industrial Parkway, Madison, WI 53704",
  },
} as const;

export function createPageMetadata({
  title,
  description,
  path = "",
}: {
  title: string;
  description: string;
  path?: string;
}): Metadata {
  const url = `${siteConfig.url}${path}`;
  return {
    title: `${title} | ${siteConfig.name}`,
    description,
    openGraph: {
      title: `${title} | ${siteConfig.name}`,
      description,
      url,
      siteName: siteConfig.name,
      type: "website",
      locale: "en_US",
      images: [{ url: siteConfig.ogImage, width: 1200, height: 630, alt: siteConfig.name }],
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} | ${siteConfig.name}`,
      description,
      images: [siteConfig.ogImage],
    },
    alternates: { canonical: url },
  };
}

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: siteConfig.name,
    url: siteConfig.url,
    description: siteConfig.description,
    telephone: siteConfig.contact.phone,
    email: siteConfig.contact.email,
    address: {
      "@type": "PostalAddress",
      streetAddress: "1200 Industrial Parkway",
      addressLocality: "Madison",
      addressRegion: "WI",
      postalCode: "53704",
      addressCountry: "US",
    },
  };
}

export function webPageJsonLd(title: string, description: string, path: string) {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: title,
    description,
    url: `${siteConfig.url}${path}`,
    isPartOf: { "@type": "WebSite", name: siteConfig.name, url: siteConfig.url },
  };
}
