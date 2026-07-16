export interface Industry {
  id: string;
  name: string;
  description: string;
  image: string;
  highlights: string[];
}

export const industries: Industry[] = [
  {
    id: "fire-departments",
    name: "Fire Departments",
    description:
      "Municipal, volunteer, and regional fire departments rely on Iron Ridge for custom apparatus that meets NFPA standards and local operational requirements.",
    image:
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop&q=80",
    highlights: ["NFPA 1901 compliance", "Fleet replacement programs", "Grant documentation support"],
  },
  {
    id: "ems",
    name: "EMS",
    description:
      "Private and municipal EMS providers choose Iron Ridge for reliable ambulances configured for ALS, BLS, and specialty transport operations.",
    image:
      "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&h=600&fit=crop&q=80",
    highlights: ["CAAS standards", "Multi-unit fleet pricing", "Fast-track delivery options"],
  },
  {
    id: "hospitals",
    name: "Hospitals",
    description:
      "Hospital systems and healthcare networks procure specialty transport and support vehicles through our streamlined institutional procurement process.",
    image:
      "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&h=600&fit=crop&q=80",
    highlights: ["Healthcare fleet standards", "Infection control features", "Multi-site delivery"],
  },
  {
    id: "industrial",
    name: "Industrial",
    description:
      "Industrial safety teams and private emergency response units depend on rugged vehicles built for demanding operational environments.",
    image:
      "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=600&fit=crop&q=80",
    highlights: ["Hazmat configurations", "Plant-specific requirements", "OSHA compliance support"],
  },
  {
    id: "military",
    name: "Military",
    description:
      "Defense and military organizations procure specialized emergency and support vehicles through compliant federal and GSA procurement channels.",
    image:
      "https://images.unsplash.com/photo-1541339907198-e08756dedf5f?w=800&h=600&fit=crop&q=80",
    highlights: ["GSA schedule eligible", "Military specifications", "Secure communications ready"],
  },
  {
    id: "airport-rescue",
    name: "Airport Rescue",
    description:
      "ARFF and airport emergency services require purpose-built vehicles meeting FAA and ICAO standards for rapid response and fire suppression.",
    image:
      "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&h=600&fit=crop&q=80",
    highlights: ["ARFF configurations", "FAA Part 139 compliance", "High-capacity foam systems"],
  },
  {
    id: "government",
    name: "Government",
    description:
      "Federal, state, and local government agencies benefit from transparent pricing, compliant documentation, and reliable delivery timelines.",
    image:
      "https://images.unsplash.com/photo-1569163139394-de446e504f12?w=800&h=600&fit=crop&q=80",
    highlights: ["Cooperative purchasing", "Bid documentation", "Multi-year fleet planning"],
  },
];
