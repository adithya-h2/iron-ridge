import { CtaBanner, PageHero, Section, VehicleCard } from "@/components/marketing";
import { vehicles } from "@/content/vehicles";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Products",
  description:
    "Browse Iron Ridge emergency vehicles — fire engines, ambulances, rescue trucks, command vehicles, and utility vehicles built to your specifications.",
  path: "/products",
});

export default function ProductsPage() {
  const jsonLd = webPageJsonLd(
    "Products",
    "Iron Ridge emergency vehicle product catalog",
    "/products"
  );

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Products"
        description="Custom emergency response vehicles engineered and manufactured to meet your department's exact requirements."
      />
      <Section>
        <div className="grid gap-8 lg:grid-cols-2">
          {vehicles.map((vehicle) => (
            <VehicleCard key={vehicle.id} vehicle={vehicle} variant="full" />
          ))}
        </div>
      </Section>
      <Section variant="muted">
        <CtaBanner
          title="Ready to configure your vehicle?"
          description="Our team will work with you to define specifications and provide a detailed quotation."
        />
      </Section>
    </>
  );
}
