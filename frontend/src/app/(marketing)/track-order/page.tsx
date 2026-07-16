import Link from "next/link";

import { PageHero, Section } from "@/components/marketing";
import { buttonVariants } from "@/components/ui/button";
import { createPageMetadata, webPageJsonLd } from "@/lib/seo";
import { cn } from "@/lib/utils";

export const metadata = createPageMetadata({
  title: "Track Order",
  description: "Track your Iron Ridge vehicle order status. Order tracking portal coming soon.",
  path: "/track-order",
});

export default function TrackOrderPage() {
  const jsonLd = webPageJsonLd("Track Order", "Iron Ridge order tracking", "/track-order");

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        title="Track Order"
        description="Order status tracking is coming soon. Contact our team for delivery updates on active orders."
      />
      <Section>
        <div className="mx-auto max-w-lg rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
          <p className="text-lg font-semibold text-charcoal">Order Tracking — Coming Soon</p>
          <p className="mt-3 text-sm text-steel">
            We are building a secure portal for customers to track production and delivery status.
            In the meantime, contact our team for updates on your order.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link href="/contact" className={cn(buttonVariants({ variant: "outline" }))}>
              Contact Us
            </Link>
            <Link
              href="/request-consultation"
              className={cn(buttonVariants(), "bg-accent-red text-white hover:bg-accent-red/90")}
            >
              Request Consultation
            </Link>
          </div>
        </div>
      </Section>
    </>
  );
}
