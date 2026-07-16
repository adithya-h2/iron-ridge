export const navLinks = [
  { href: "/", label: "Home" },
  { href: "/products", label: "Products" },
  { href: "/industries", label: "Industries" },
  { href: "/process", label: "Process" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
] as const;

export const footerColumns = {
  products: [
    { href: "/products", label: "All Vehicles" },
    { href: "/products#fire-engines", label: "Fire Engines" },
    { href: "/products#ambulances", label: "Ambulances" },
    { href: "/products#rescue-trucks", label: "Rescue Trucks" },
  ],
  industries: [
    { href: "/industries", label: "All Industries" },
    { href: "/industries#fire-departments", label: "Fire Departments" },
    { href: "/industries#ems", label: "EMS" },
    { href: "/industries#hospitals", label: "Hospitals" },
  ],
  resources: [
    { href: "/process", label: "Procurement Process" },
    { href: "/track-order", label: "Track Order" },
    { href: "/about", label: "About Us" },
  ],
  support: [
    { href: "/contact", label: "Contact" },
    { href: "/request-consultation", label: "Request Consultation" },
    { href: "tel:+18005550199", label: "+1 (800) 555-0199" },
  ],
  legal: [
    { href: "/privacy", label: "Privacy Policy" },
    { href: "/terms", label: "Terms of Service" },
  ],
} as const;

export const contactInfo = {
  office: "1200 Industrial Parkway, Madison, WI 53704",
  phone: "+1 (800) 555-0199",
  email: "sales@ironridgevehicles.com",
  hours: "Monday – Friday, 7:00 AM – 6:00 PM CST",
  linkedIn: "https://www.linkedin.com/company/iron-ridge",
} as const;

export const companyStats = [
  { label: "Years Experience", value: "35+" },
  { label: "Vehicles Delivered", value: "4,200+" },
  { label: "Departments Served", value: "850+" },
  { label: "Average Delivery Time", value: "14 Weeks" },
] as const;

export const trustedBy = [
  "Fire Departments",
  "Hospitals",
  "EMS",
  "Municipalities",
  "Government",
] as const;

export const whyIronRidge = [
  {
    title: "Custom Engineering",
    description:
      "Every vehicle is engineered to your department's specifications, apparatus requirements, and operational standards.",
  },
  {
    title: "Rapid Procurement",
    description:
      "Streamlined quoting and approval processes help you move from requirements to production without unnecessary delays.",
  },
  {
    title: "Certified Manufacturing",
    description:
      "NFPA-compliant production with rigorous quality control at every stage of assembly and inspection.",
  },
  {
    title: "End-to-End Delivery",
    description:
      "From initial consultation through final delivery and commissioning, we manage the complete procurement lifecycle.",
  },
] as const;

export const aboutSections = [
  {
    title: "Mission",
    description:
      "Iron Ridge builds emergency response vehicles that help first responders save lives. We combine American manufacturing excellence with a procurement process designed for speed, transparency, and reliability.",
  },
  {
    title: "Manufacturing",
    description:
      "Our 180,000 sq ft facility in Wisconsin produces custom fire apparatus, ambulances, and specialty vehicles using certified components and proven assembly methods.",
  },
  {
    title: "Engineering",
    description:
      "In-house engineering teams work directly with your department to configure chassis, body, equipment mounts, and electrical systems to your exact requirements.",
  },
  {
    title: "Quality",
    description:
      "Multi-point inspection protocols, road testing, and third-party certification ensure every vehicle meets or exceeds industry standards before delivery.",
  },
  {
    title: "Safety",
    description:
      "Occupant safety, structural integrity, and operational reliability are designed into every vehicle from the first engineering review.",
  },
  {
    title: "Compliance",
    description:
      "All vehicles are built to NFPA, DOT, and applicable state EMS standards with full documentation for procurement and audit requirements.",
  },
] as const;
