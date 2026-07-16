"use client";

import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";

import { ErrorAlert } from "@/components/common/error-alert";
import { FormInput } from "@/components/forms/form-input";
import { FormSelect } from "@/components/forms/form-select";
import { FormTextarea } from "@/components/forms/form-textarea";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  budgetOptions,
  consultationFormSchema,
  timelineOptions,
  toLeadPayload,
  vehicleTypeOptions,
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
      department: "",
      contact_person: "",
      email: "",
      phone: "",
      city: "",
      state: "",
      vehicle_type: "",
      required_quantity: 1,
      expected_timeline: "",
      budget_range: "",
      notes: "",
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

  if (mutation.isSuccess && mutation.data) {
    return (
      <Card ref={successRef} tabIndex={-1} aria-live="polite">
        <CardHeader>
          <CardTitle className="text-success">Consultation Request Received</CardTitle>
          <CardDescription>
            Thank you for contacting Iron Ridge. A member of our team will reach out within one
            business day.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-steel">
          <p>
            <span className="font-medium text-charcoal">Reference ID:</span>{" "}
            {mutation.data.deal_id}
          </p>
          {mutation.data.is_duplicate ? (
            <p className="text-accent-orange">
              We found an existing record for your organization and have linked this request
              accordingly.
            </p>
          ) : null}
        </CardContent>
      </Card>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-8" noValidate>
        {mutation.isError ? (
          <ErrorAlert
            title="Unable to submit request"
            message={mutation.error.message ?? "Please try again or contact us directly."}
          />
        ) : null}

        <fieldset className="space-y-4">
          <legend className="text-lg font-bold text-charcoal">Organization</legend>
          <div className="grid gap-4 md:grid-cols-2">
            <FormInput control={form.control} name="company_name" label="Organization" />
            <FormInput control={form.control} name="department" label="Department" />
          </div>
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-lg font-bold text-charcoal">Contact Information</legend>
          <div className="grid gap-4 md:grid-cols-2">
            <FormInput control={form.control} name="contact_person" label="Contact Person" />
            <FormInput control={form.control} name="email" label="Email" type="email" />
            <FormInput control={form.control} name="phone" label="Phone" type="tel" />
          </div>
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-lg font-bold text-charcoal">Location</legend>
          <div className="grid gap-4 md:grid-cols-2">
            <FormInput control={form.control} name="city" label="City" />
            <FormInput control={form.control} name="state" label="State" />
          </div>
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-lg font-bold text-charcoal">Vehicle Requirements</legend>
          <div className="grid gap-4 md:grid-cols-2">
            <FormSelect
              control={form.control}
              name="vehicle_type"
              label="Vehicle Type"
              options={[...vehicleTypeOptions]}
            />
            <FormField
              control={form.control}
              name="required_quantity"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Quantity</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1}
                      {...field}
                      onChange={(e) => field.onChange(e.target.valueAsNumber || 1)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormSelect
              control={form.control}
              name="expected_timeline"
              label="Expected Timeline"
              options={[...timelineOptions]}
            />
            <FormSelect
              control={form.control}
              name="budget_range"
              label="Budget Range (Optional)"
              options={[...budgetOptions]}
            />
          </div>
          <FormTextarea
            control={form.control}
            name="notes"
            label="Additional Notes"
            placeholder="Describe specific requirements, apparatus standards, or fleet considerations..."
          />
        </fieldset>

        <Button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-accent-red text-white hover:bg-accent-red/90 md:w-auto"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            "Submit Consultation Request"
          )}
        </Button>
      </form>
    </Form>
  );
}
