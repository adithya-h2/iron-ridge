import { CtaBanner, IndustryCard, PageHero, Section } from "@/components/marketing";
import { industries } from "@/content/industries";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Industries",
  description:
    "Iron Ridge serves fire departments, EMS, hospitals, industrial safety, military, airport rescue, and government organizations across the United States.",
  path: "/industries",
});

export default function IndustriesPage() {
  const jsonLd = webPageJsonLd(
    "Industries",
    "Industries served by Iron Ridge emergency vehicles",
    "/industries"
  );

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Industries"
        description="Purpose-built emergency vehicles for the organizations that protect our communities."
      />
      <Section>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {industries.map((industry) => (
            <IndustryCard key={industry.id} industry={industry} />
          ))}
        </div>
      </Section>
      <Section variant="muted">
        <CtaBanner />
      </Section>
    </>
  );
}
