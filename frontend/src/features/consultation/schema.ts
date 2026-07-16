import { z } from "zod";


export const consultationFormSchema = z.object({
  company_name: z.string().min(1, "Organization Name is required"),
  org_type: z.string().min(1, "Organization Type is required"),
  department: z.string().optional(),
  website: z.string().optional(),
  contact_person: z.string().min(1, "Contact Person is required"),
  job_title: z.string().optional(),
  email: z.string().min(1, "Business Email is required").email("Enter a valid email address"),
  phone: z.string()
    .min(1, "Phone Number is required")
    .regex(/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im, "Enter a valid phone number"),
  preferred_contact_method: z.string().optional(),
  country: z.string().min(1, "Country is required"),
  state: z.string().min(1, "State is required"),
  city: z.string().min(1, "City is required"),
  vehicle_type: z.string().min(1, "Vehicle Category is required"),
  required_quantity: z.string().min(1, "Estimated Quantity is required"),
  expected_timeline: z.string().min(1, "Purchase Timeline is required"),
  notes: z.string().max(500, "Brief description must be 500 characters or less").optional(),
  consent: z.boolean().refine((val) => val === true, {
    message: "You must agree that Iron Ridge may contact you to proceed",
  }),
});

export type ConsultationFormValues = z.infer<typeof consultationFormSchema>;

export const orgTypeOptions = [
  { label: "Hospital", value: "Hospital" },
  { label: "Health System", value: "Health System" },
  { label: "EMS Provider", value: "EMS Provider" },
  { label: "Fire Department", value: "Fire Department" },
  { label: "Municipality", value: "Municipality" },
  { label: "Airport", value: "Airport" },
  { label: "Government Agency", value: "Government Agency" },
  { label: "Private Company", value: "Private Company" },
  { label: "Other", value: "Other" },
] as const;

export const preferredContactMethodOptions = [
  { label: "Email", value: "Email" },
  { label: "Phone", value: "Phone" },
  { label: "Either", value: "Either" },
] as const;

export const vehicleCategoryOptions = [
  { label: "Ambulance", value: "Ambulance" },
  { label: "Fire Engine", value: "Fire Engine" },
  { label: "Rescue Vehicle", value: "Rescue Vehicle" },
  { label: "Mobile Medical Unit", value: "Mobile Medical Unit" },
  { label: "Police Vehicle", value: "Police Vehicle" },
  { label: "Utility Vehicle", value: "Utility Vehicle" },
  { label: "Other", value: "Other" },
] as const;

export const quantityOptions = [
  { label: "1", value: "1" },
  { label: "2–5", value: "2–5" },
  { label: "6–10", value: "6–10" },
  { label: "10+", value: "10+" },
] as const;

export const purchaseTimelineOptions = [
  { label: "Immediate", value: "Immediate" },
  { label: "Within 3 Months", value: "Within 3 Months" },
  { label: "Within 6 Months", value: "Within 6 Months" },
  { label: "Within 12 Months", value: "Within 12 Months" },
  { label: "Planning Stage", value: "Planning Stage" },
] as const;

function mapQuantityToInteger(qty: string): number {
  if (qty === "2–5" || qty === "2-5") return 2;
  if (qty === "6–10" || qty === "6-10") return 6;
  if (qty === "10+") return 10;
  return parseInt(qty, 10) || 1;
}

export function toLeadPayload(values: ConsultationFormValues) {
  const quantityInt = mapQuantityToInteger(values.required_quantity);
  
  const noteParts = [
    values.notes?.trim() ? `Operational Needs: ${values.notes.trim()}` : "",
    values.department ? `Department: ${values.department}` : "",
    values.job_title ? `Job Title: ${values.job_title}` : "",
    values.preferred_contact_method ? `Preferred Contact Method: ${values.preferred_contact_method}` : "",
    `Estimated Quantity: ${values.required_quantity}`,
    `Purchase Timeline: ${values.expected_timeline}`,
  ].filter(Boolean);

  return {
    source: "WEBSITE" as const,
    submission_channel: "web_form" as const,
    company_name: values.company_name,
    contact_person: values.contact_person,
    email: values.email,
    phone: values.phone,
    website: values.website || undefined,
    city: values.city,
    state: values.state,
    country: values.country,
    industry: values.org_type,
    vehicle_type: values.vehicle_type,
    required_quantity: quantityInt,
    notes: noteParts.join("\n") || undefined,
    department: values.department || undefined,
    expected_timeline: values.expected_timeline,
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
