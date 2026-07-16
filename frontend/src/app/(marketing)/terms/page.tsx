import { PageHero, Section } from "@/components/marketing";
import { createPageMetadata } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Terms of Service",
  description: "Iron Ridge website terms of service.",
  path: "/terms",
});

export default function TermsPage() {
  return (
    <>
      <PageHero title="Terms of Service" />
      <Section>
        <div className="mx-auto max-w-3xl text-steel">
          <p>
            Use of this website is subject to Iron Ridge terms and conditions. Product
            specifications, pricing, and delivery timelines provided through this site are
            estimates and subject to formal quotation and contract.
          </p>
          <p className="mt-4">
            For legal inquiries, contact{" "}
            <a href="mailto:legal@ironridgevehicles.com" className="text-accent-red hover:underline">
              legal@ironridgevehicles.com
            </a>
            .
          </p>
        </div>
      </Section>
    </>
  );
}
