import { z } from "zod";

export const consultationFormSchema = z.object({
  company_name: z.string().min(2, "Organization name is required"),
  department: z.string().min(1, "Department is required"),
  contact_person: z.string().min(2, "Contact person is required"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(10, "Enter a valid phone number"),
  city: z.string().min(2, "City is required"),
  state: z.string().min(2, "State is required"),
  vehicle_type: z.string().min(1, "Select a vehicle type"),
  required_quantity: z.number().int().min(1, "Quantity must be at least 1"),
  expected_timeline: z.string().min(1, "Expected timeline is required"),
  budget_range: z.string().optional(),
  notes: z.string().optional(),
});

export type ConsultationFormValues = z.infer<typeof consultationFormSchema>;

export const vehicleTypeOptions = [
  { label: "Fire Engine", value: "Fire Engine" },
  { label: "Ambulance", value: "Ambulance" },
  { label: "Rescue Truck", value: "Rescue Truck" },
  { label: "Command Vehicle", value: "Command Vehicle" },
  { label: "Utility Vehicle", value: "Utility Vehicle" },
  { label: "Other / Custom", value: "Other" },
] as const;

export const timelineOptions = [
  { label: "Immediate (0–3 months)", value: "0-3 months" },
  { label: "Near-term (3–6 months)", value: "3-6 months" },
  { label: "Planning (6–12 months)", value: "6-12 months" },
  { label: "Future (12+ months)", value: "12+ months" },
] as const;

export const budgetOptions = [
  { label: "Under $250,000", value: "under-250k" },
  { label: "$250,000 – $500,000", value: "250k-500k" },
  { label: "$500,000 – $1,000,000", value: "500k-1m" },
  { label: "Over $1,000,000", value: "over-1m" },
  { label: "Not sure yet", value: "unsure" },
] as const;

export function toLeadPayload(values: ConsultationFormValues) {
  const noteParts = [
    values.notes?.trim(),
    values.expected_timeline ? `Expected timeline: ${values.expected_timeline}` : "",
    values.budget_range ? `Budget range: ${values.budget_range}` : "",
  ].filter(Boolean);

  return {
    source: "WEBSITE" as const,
    submission_channel: "web_form" as const,
    company_name: values.company_name,
    department: values.department,
    industry: values.department,
    contact_person: values.contact_person,
    email: values.email,
    phone: values.phone,
    city: values.city,
    state: values.state,
    country: "USA",
    vehicle_type: values.vehicle_type,
    required_quantity: values.required_quantity,
    expected_timeline: values.expected_timeline,
    budget_range: values.budget_range,
    notes: noteParts.join("\n") || undefined,
  };
}

export const contactFormSchema = z.object({
  company_name: z.string().min(2, "Organization name is required"),
  contact_person: z.string().min(2, "Name is required"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().optional(),
  notes: z.string().min(10, "Please include a brief message"),
});

export type ContactFormValues = z.infer<typeof contactFormSchema>;

export function toContactLeadPayload(values: ContactFormValues) {
  return {
    source: "WEBSITE" as const,
    submission_channel: "contact_form" as const,
    company_name: values.company_name,
    contact_person: values.contact_person,
    email: values.email,
    phone: values.phone,
    country: "USA",
    notes: values.notes,
  };
}
