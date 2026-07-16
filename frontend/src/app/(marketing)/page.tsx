import {
  CtaBanner,
  FeatureCard,
  Hero,
  ProcurementTimeline,
  Section,
  SlideUp,
  StatsRow,
  StaggerChildren,
  StaggerItem,
  TrustedBy,
  VehicleCard,
} from "@/components/marketing";
import { companyStats, whyIronRidge } from "@/content/site";
import { processSteps } from "@/content/process-steps";
import { heroImage, vehicles } from "@/content/vehicles";
import { organizationJsonLd } from "@/lib/seo";

export default function HomePage() {
  const jsonLd = organizationJsonLd();

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Hero
        headline="Emergency Vehicles. Built Faster. Delivered Smarter."
        subheading="From consultation to delivery, our structured procurement process helps organizations acquire emergency vehicles with confidence."
        image={heroImage}
      />

      <Section className="py-12 md:py-16">
        <TrustedBy />
      </Section>

      <Section variant="muted">
        <SlideUp>
          <div className="text-center">
            <h2 className="text-3xl font-bold text-charcoal md:text-4xl">Why Iron Ridge</h2>
            <p className="mx-auto mt-4 max-w-2xl text-steel">
              Trusted by departments across the United States for custom engineering, certified
              manufacturing, and reliable delivery.
            </p>
          </div>
        </SlideUp>
        <StaggerChildren className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {whyIronRidge.map((item) => (
            <StaggerItem key={item.title}>
              <FeatureCard title={item.title} description={item.description} />
            </StaggerItem>
          ))}
        </StaggerChildren>
      </Section>

      <Section>
        <SlideUp>
          <div className="text-center">
            <h2 className="text-3xl font-bold text-charcoal md:text-4xl">Vehicle Categories</h2>
            <p className="mx-auto mt-4 max-w-2xl text-steel">
              Custom-built emergency response vehicles for every mission profile.
            </p>
          </div>
        </SlideUp>
        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {vehicles.slice(0, 5).map((vehicle) => (
            <VehicleCard key={vehicle.id} vehicle={vehicle} />
          ))}
        </div>
      </Section>

      <Section variant="muted">
        <SlideUp>
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-charcoal md:text-4xl">Procurement Process</h2>
            <p className="mx-auto mt-4 max-w-2xl text-steel">
              A clear, structured path from first conversation to vehicle delivery.
            </p>
          </div>
        </SlideUp>
        <ProcurementTimeline steps={processSteps} />
      </Section>

      <Section>
        <StatsRow stats={companyStats} />
      </Section>

      <Section variant="muted">
        <CtaBanner />
      </Section>
    </>
  );
}
