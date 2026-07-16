import { Suspense } from "react";

import { ConsultationForm } from "@/features/consultation";
import { PageHero, Section } from "@/components/marketing";
import { LoadingSpinner } from "@/components/common/loading-spinner";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Request Consultation",
  description:
    "Request a consultation with Iron Ridge for custom emergency vehicle procurement. Tell us about your organization, requirements, and timeline.",
  path: "/request-consultation",
});

export default function RequestConsultationPage() {
  const jsonLd = webPageJsonLd(
    "Request Consultation",
    "Request a consultation with Iron Ridge",
    "/request-consultation"
  );

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Request Consultation"
        description="Tell us about your organization and vehicle requirements. Our team will respond within one business day."
      />
      <Section>
        <div className="mx-auto max-w-3xl rounded-xl border border-border bg-white p-6 md:p-10">
          <Suspense fallback={<LoadingSpinner label="Loading form..." />}>
            <ConsultationForm />
          </Suspense>
        </div>
      </Section>
    </>
  );
}
