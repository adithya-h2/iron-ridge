import { ContactForm } from "@/features/consultation";
import { CtaBanner, PageHero, Section } from "@/components/marketing";
import { contactInfo } from "@/content/site";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";
import { Mail, MapPin, Phone } from "lucide-react";

export const metadata = createPageMetadata({
  title: "Contact",
  description:
    "Contact Iron Ridge for emergency vehicle inquiries. Madison, WI headquarters. Call +1 (800) 555-0199 or email sales@ironridgevehicles.com.",
  path: "/contact",
});

export default function ContactPage() {
  const jsonLd = webPageJsonLd("Contact", "Contact Iron Ridge", "/contact");

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Contact Us"
        description="Reach our team for sales inquiries, fleet consultations, and general questions."
      />
      <Section>
        <div className="grid gap-12 lg:grid-cols-2">
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold text-charcoal">Office</h2>
              <div className="mt-3 flex items-start gap-3 text-steel">
                <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-accent-red" aria-hidden />
                <p>{contactInfo.office}</p>
              </div>
            </div>
            <div>
              <h2 className="text-xl font-bold text-charcoal">Phone</h2>
              <a
                href={`tel:${contactInfo.phone.replace(/\D/g, "")}`}
                className="mt-3 flex items-center gap-3 text-steel hover:text-accent-red"
              >
                <Phone className="h-5 w-5 shrink-0 text-accent-red" aria-hidden />
                {contactInfo.phone}
              </a>
            </div>
            <div>
              <h2 className="text-xl font-bold text-charcoal">Email</h2>
              <a
                href={`mailto:${contactInfo.email}`}
                className="mt-3 flex items-center gap-3 text-steel hover:text-accent-red"
              >
                <Mail className="h-5 w-5 shrink-0 text-accent-red" aria-hidden />
                {contactInfo.email}
              </a>
            </div>
            <div>
              <h2 className="text-xl font-bold text-charcoal">Business Hours</h2>
              <p className="mt-3 text-steel">{contactInfo.hours}</p>
            </div>
            <div className="overflow-hidden rounded-xl border border-border">
              <iframe
                title="Iron Ridge office location"
                src="https://maps.google.com/maps?q=Madison+WI&t=&z=13&ie=UTF8&iwloc=&output=embed"
                className="h-64 w-full"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
          </div>
          <div className="rounded-xl border border-border bg-white p-6 md:p-8">
            <h2 className="text-xl font-bold text-charcoal">Send a Message</h2>
            <p className="mt-2 text-sm text-steel">
              For detailed fleet requirements, use our{" "}
              <a href="/request-consultation" className="text-accent-red hover:underline">
                consultation form
              </a>
              .
            </p>
            <div className="mt-6">
              <ContactForm />
            </div>
          </div>
        </div>
      </Section>
      <Section variant="muted">
        <CtaBanner />
      </Section>
    </>
  );
}
