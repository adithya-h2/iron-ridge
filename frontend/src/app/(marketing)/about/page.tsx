import { CtaBanner, FeatureCard, PageHero, Section, StaggerChildren, StaggerItem } from "@/components/marketing";
import { aboutSections } from "@/content/site";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "About",
  description:
    "Iron Ridge is an American manufacturer of emergency response vehicles with 35+ years of experience in custom engineering, certified manufacturing, and nationwide delivery.",
  path: "/about",
});

export default function AboutPage() {
  const jsonLd = webPageJsonLd("About", "About Iron Ridge emergency vehicle manufacturing", "/about");

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="About Iron Ridge"
        description="American manufacturing excellence for the departments that serve our communities."
      />
      <Section>
        <StaggerChildren className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {aboutSections.map((section) => (
            <StaggerItem key={section.title}>
              <FeatureCard title={section.title} description={section.description} />
            </StaggerItem>
          ))}
        </StaggerChildren>
      </Section>
      <Section variant="muted">
        <CtaBanner />
      </Section>
    </>
  );
}
