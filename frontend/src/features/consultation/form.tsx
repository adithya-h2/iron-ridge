"use client";

import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Check } from "lucide-react";
import Link from "next/link";

import { ErrorAlert } from "@/components/common/error-alert";
import { FormInput, FormCheckbox, FormSelect, FormTextarea } from "@/components/forms";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import {
  consultationFormSchema,
  toLeadPayload,
  orgTypeOptions,
  preferredContactMethodOptions,
  vehicleCategoryOptions,
  quantityOptions,
  purchaseTimelineOptions,
  type ConsultationFormValues,
} from "@/features/consultation/schema";
import { useSubmitLead } from "@/features/consultation/use-submit-lead";

export function ConsultationForm() {
  const searchParams = useSearchParams();
  const successRef = useRef<HTMLDivElement>(null);
  const mutation = useSubmitLead();

  const form = useForm<ConsultationFormValues>({
    resolver: zodResolver(consultationFormSchema),
    defaultValues: {
      company_name: "",
      org_type: "",
      department: "",
      website: "",
      contact_person: "",
      job_title: "",
      email: "",
      phone: "",
      preferred_contact_method: "",
      country: "",
      state: "",
      city: "",
      vehicle_type: "",
      required_quantity: "",
      expected_timeline: "",
      notes: "",
      consent: false,
    },
  });

  useEffect(() => {
    const vehicle = searchParams.get("vehicle");
    if (vehicle) {
      form.setValue("vehicle_type", vehicle);
    }
  }, [searchParams, form]);

  useEffect(() => {
    if (mutation.isSuccess && successRef.current) {
      successRef.current.focus();
    }
  }, [mutation.isSuccess]);

  const onSubmit = form.handleSubmit(async (values) => {
    await mutation.mutateAsync(toLeadPayload(values));
  });

  const notesValue = form.watch("notes") || "";

  if (mutation.isSuccess && mutation.data) {
    return (
      <Card
        ref={successRef}
        tabIndex={-1}
        aria-live="polite"
        className="mx-auto max-w-xl text-center border-none shadow-none bg-transparent"
      >
        <CardHeader className="space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400">
            <Check className="h-7 w-7" />
          </div>
          <CardTitle className="text-3xl font-extrabold text-charcoal tracking-tight">
            Thank You
          </CardTitle>
          <CardDescription className="text-base text-steel leading-relaxed">
            Thank you for your interest in Iron Ridge.
            <br />
            Our team will review your request, verify your organization, and contact you shortly.
            <br />
            If your requirements match our solutions, one of our specialists will guide you through
            the next stage of the consultation process.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 pt-2">
          <div className="bg-slate-50 border border-slate-100 rounded-lg p-4 inline-block text-sm space-y-1 text-steel">
            <p>
              <span className="font-medium text-charcoal">Reference ID:</span>{" "}
              <code className="text-accent-red font-mono font-bold">{mutation.data.deal_id}</code>
            </p>
            {mutation.data.is_duplicate ? (
              <p className="text-accent-orange font-medium mt-1 text-xs">
                An existing record was found for your organization and this request has been linked.
              </p>
            ) : null}
          </div>
          <div className="pt-2">
            <Link href="/" passHref legacyBehavior>
              <Button className="px-8 py-3 bg-accent-red text-white hover:bg-accent-red/90 transition-colors font-medium rounded-md shadow-md hover:shadow-lg cursor-pointer">
                Return Home
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-10" noValidate>
        {mutation.isError ? (
          <ErrorAlert
            title="Unable to submit request"
            message={mutation.error.message ?? "Please try again or contact us directly."}
          />
        ) : null}

        {/* Section 1: Organization Information */}
        <fieldset className="space-y-6">
          <legend className="text-xl font-bold text-charcoal tracking-tight">
            1. Organization Information
          </legend>
          <div className="grid gap-6 md:grid-cols-2">
            <FormInput
              control={form.control}
              name="company_name"
              label="Organization Name *"
              placeholder="e.g. City Fire Department"
            />
            <FormSelect
              control={form.control}
              name="org_type"
              label="Organization Type *"
              options={[...orgTypeOptions]}
              placeholder="Select organization type..."
            />
            <FormInput
              control={form.control}
              name="department"
              label="Department (Optional)"
              placeholder="e.g. Fleet Procurement"
            />
            <FormInput
              control={form.control}
              name="website"
              label="Website (Optional)"
              placeholder="e.g. www.cityfire.org"
            />
          </div>
        </fieldset>

        {/* Section 2: Contact Information */}
        <fieldset className="space-y-6 border-t border-slate-100 pt-8">
          <legend className="text-xl font-bold text-charcoal tracking-tight">
            2. Contact Information
          </legend>
          <div className="grid gap-6 md:grid-cols-2">
            <FormInput
              control={form.control}
              name="contact_person"
              label="Contact Person *"
              placeholder="e.g. Chief John Doe"
            />
            <FormInput
              control={form.control}
              name="job_title"
              label="Job Title (Optional)"
              placeholder="e.g. Fleet Manager"
            />
            <FormInput
              control={form.control}
              name="email"
              label="Business Email *"
              type="email"
              placeholder="e.g. jdoe@cityfire.org"
            />
            <FormInput
              control={form.control}
              name="phone"
              label="Phone Number *"
              type="tel"
              placeholder="e.g. (555) 123-4567"
            />
            <div className="md:col-span-2">
              <div className="max-w-md">
                <FormSelect
                  control={form.control}
                  name="preferred_contact_method"
                  label="Preferred Contact Method (Optional)"
                  options={[...preferredContactMethodOptions]}
                  placeholder="Select preferred method..."
                />
              </div>
            </div>
          </div>
        </fieldset>

        {/* Section 3: Location */}
        <fieldset className="space-y-6 border-t border-slate-100 pt-8">
          <legend className="text-xl font-bold text-charcoal tracking-tight">
            3. Location
          </legend>
          <div className="grid gap-6 md:grid-cols-3">
            <FormInput
              control={form.control}
              name="country"
              label="Country *"
              placeholder="e.g. USA"
            />
            <FormInput
              control={form.control}
              name="state"
              label="State *"
              placeholder="e.g. TX"
            />
            <FormInput
              control={form.control}
              name="city"
              label="City *"
              placeholder="e.g. Austin"
            />
          </div>
        </fieldset>

        {/* Section 4: Purchase Interest */}
        <fieldset className="space-y-6 border-t border-slate-100 pt-8">
          <legend className="text-xl font-bold text-charcoal tracking-tight">
            4. Purchase Interest
          </legend>
          <div className="grid gap-6 md:grid-cols-3">
            <FormSelect
              control={form.control}
              name="vehicle_type"
              label="Vehicle Category *"
              options={[...vehicleCategoryOptions]}
              placeholder="Select category..."
            />
            <FormSelect
              control={form.control}
              name="required_quantity"
              label="Estimated Quantity *"
              options={[...quantityOptions]}
              placeholder="Select quantity..."
            />
            <FormSelect
              control={form.control}
              name="expected_timeline"
              label="Purchase Timeline *"
              options={[...purchaseTimelineOptions]}
              placeholder="Select timeline..."
            />
          </div>
        </fieldset>

        {/* Section 5: About Your Requirement */}
        <fieldset className="space-y-4 border-t border-slate-100 pt-8">
          <legend className="text-xl font-bold text-charcoal tracking-tight">
            5. About Your Requirement
          </legend>
          <FormField
            control={form.control}
            name="notes"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Requirement Details (Optional)</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Briefly describe your operational needs or what prompted your interest."
                    maxLength={500}
                    className="min-h-32 resize-none"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="text-right text-xs text-steel">
            {notesValue.length} / 500 characters
          </div>
        </fieldset>

        {/* Section 6: Consent */}
        <fieldset className="space-y-4 border-t border-slate-100 pt-8">
          <legend className="sr-only">Consent</legend>
          <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-4 transition-colors hover:bg-slate-50">
            <FormCheckbox
              control={form.control}
              name="consent"
              label="I agree that Iron Ridge may contact me regarding this consultation request. *"
            />
          </div>
        </fieldset>

        {/* Submit Button */}
        <div className="pt-6 border-t border-slate-100 flex justify-end">
          <Button
            type="submit"
            disabled={mutation.isPending}
            className="w-full md:w-auto px-8 py-4 bg-accent-red text-white hover:bg-accent-red/90 active:scale-[0.98] transition-all font-semibold rounded-md shadow-md hover:shadow-lg flex items-center justify-center gap-2 cursor-pointer"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Submitting...
              </>
            ) : (
              "Request Consultation"
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
}
