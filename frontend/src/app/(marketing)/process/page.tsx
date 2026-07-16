import { CtaBanner, PageHero, ProcurementTimeline, Section, SlideUp } from "@/components/marketing";
import { processSteps } from "@/content/process-steps";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Procurement Process",
  description:
    "Learn how Iron Ridge guides your organization from initial consultation through engineering, quotation, approval, production, and delivery.",
  path: "/process",
});

export default function ProcessPage() {
  const jsonLd = webPageJsonLd(
    "Procurement Process",
    "Iron Ridge vehicle procurement process",
    "/process"
  );

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Procurement Process"
        description="A transparent, structured process designed for municipal and institutional procurement requirements."
      />
      <Section>
        <ProcurementTimeline steps={processSteps} variant="vertical" />
      </Section>
      <Section variant="muted">
        <SlideUp>
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-2xl font-bold text-charcoal md:text-3xl">
              Built for procurement teams
            </h2>
            <p className="mt-4 text-steel">
              Every step includes clear documentation, progress updates, and dedicated support from
              our sales and engineering teams. We understand bid requirements, approval cycles, and
              delivery commitments — because we work with procurement officers every day.
            </p>
          </div>
        </SlideUp>
      </Section>
      <Section>
        <CtaBanner />
      </Section>
    </>
  );
}
