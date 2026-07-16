export interface ProcessStep {
  id: string;
  title: string;
  description: string;
}

export const processSteps: ProcessStep[] = [
  {
    id: "consultation",
    title: "Consultation",
    description:
      "We meet with your team to understand operational requirements, fleet standards, and procurement timeline.",
  },
  {
    id: "requirements",
    title: "Requirements",
    description:
      "Detailed specifications are documented including chassis, body configuration, equipment, and compliance standards.",
  },
  {
    id: "engineering",
    title: "Engineering",
    description:
      "Our engineering team develops custom drawings and configuration packages for your review and approval.",
  },
  {
    id: "quotation",
    title: "Quotation",
    description:
      "Transparent pricing with itemized specifications, delivery timeline, and warranty terms for procurement review.",
  },
  {
    id: "approval",
    title: "Approval",
    description:
      "Your procurement team reviews and approves the quotation through your standard authorization process.",
  },
  {
    id: "production",
    title: "Production",
    description:
      "Certified manufacturing begins with regular progress updates and quality checkpoints throughout assembly.",
  },
  {
    id: "delivery",
    title: "Delivery",
    description:
      "Final inspection, road testing, and delivery to your facility with commissioning support and documentation.",
  },
];
