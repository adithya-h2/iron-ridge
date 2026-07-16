"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";

import { ErrorAlert } from "@/components/common/error-alert";
import { FormInput } from "@/components/forms/form-input";
import { FormTextarea } from "@/components/forms/form-textarea";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import {
  contactFormSchema,
  toContactLeadPayload,
  type ContactFormValues,
} from "@/features/consultation/schema";
import { useSubmitLead } from "@/features/consultation/use-submit-lead";

export function ContactForm() {
  const mutation = useSubmitLead();
  const form = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      company_name: "",
      contact_person: "",
      email: "",
      phone: "",
      notes: "",
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    await mutation.mutateAsync(toContactLeadPayload(values));
    form.reset();
  });

  if (mutation.isSuccess) {
    return (
      <Card aria-live="polite">
        <CardHeader>
          <CardTitle className="text-success">Message Sent</CardTitle>
          <CardDescription>We will respond within one business day.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        {mutation.isError ? (
          <ErrorAlert message={mutation.error.message ?? "Unable to send message."} />
        ) : null}
        <FormInput control={form.control} name="company_name" label="Organization" />
        <FormInput control={form.control} name="contact_person" label="Your Name" />
        <FormInput control={form.control} name="email" label="Email" type="email" />
        <FormInput control={form.control} name="phone" label="Phone (Optional)" type="tel" />
        <FormTextarea control={form.control} name="notes" label="Message" />
        <Button
          type="submit"
          disabled={mutation.isPending}
          className="bg-accent-red text-white hover:bg-accent-red/90"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Sending...
            </>
          ) : (
            "Send Message"
          )}
        </Button>
      </form>
    </Form>
  );
}
