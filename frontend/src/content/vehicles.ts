export interface VehicleCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  image: string;
  specs: string[];
  features: string[];
}

export const vehicles: VehicleCategory[] = [
  {
    id: "fire-engines",
    name: "Fire Engines",
    slug: "fire-engines",
    description:
      "Custom pumper and ladder apparatus built on proven chassis platforms with NFPA-compliant configurations for municipal and rural fire departments.",
    image:
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=800&fit=crop&q=80",
    specs: ["1500–2000 GPM pumps", "500–750 gallon tanks", "Custom compartment layouts"],
    features: ["NFPA 1901 compliant", "Custom hose beds", "LED warning systems"],
  },
  {
    id: "ambulances",
    name: "Ambulances",
    slug: "ambulances",
    description:
      "Type I, II, and III ambulances configured for ALS and BLS operations with ergonomic patient compartments and durable construction.",
    image:
      "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&h=800&fit=crop&q=80",
    specs: ["Type I / II / III configurations", "ALS & BLS layouts", "Society of Automotive Engineers compliant"],
    features: ["Anti-microbial surfaces", "Climate-controlled patient area", "Integrated power systems"],
  },
  {
    id: "rescue-trucks",
    name: "Rescue Trucks",
    slug: "rescue-trucks",
    description:
      "Heavy rescue and technical rescue vehicles equipped for extrication, hazmat support, and specialized emergency operations.",
    image:
      "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&h=800&fit=crop&q=80",
    specs: ["Heavy-duty chassis", "Custom tool mounting", "Generator & lighting packages"],
    features: ["Extrication-ready storage", "Scene lighting systems", "Modular compartment design"],
  },
  {
    id: "command-vehicles",
    name: "Command Vehicles",
    slug: "command-vehicles",
    description:
      "Mobile command centers for incident management, communications coordination, and multi-agency response operations.",
    image:
      "https://images.unsplash.com/photo-1541339907198-e08756dedf5f?w=1200&h=800&fit=crop&q=80",
    specs: ["Expandable workspaces", "Integrated communications", "Climate-controlled operations center"],
    features: ["Satellite connectivity ready", "Conference seating", "Secure equipment storage"],
  },
  {
    id: "utility-vehicles",
    name: "Utility Vehicles",
    slug: "utility-vehicles",
    description:
      "Support and utility vehicles for airport rescue, industrial safety, and municipal fleet operations requiring specialized configurations.",
    image:
      "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&h=800&fit=crop&q=80",
    specs: ["4x4 configurations", "Custom utility bodies", "Towing & recovery options"],
    features: ["All-terrain capability", "Custom rack systems", "Fleet-standard paint programs"],
  },
];

export const heroImage =
  "https://images.unsplash.com/photo-1568605117037-028005066b82?w=1920&h=1080&fit=crop&q=80";
