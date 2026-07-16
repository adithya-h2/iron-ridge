import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { SlideUp } from "./motion";

interface CtaBannerProps {
  title?: string;
  description?: string;
  ctaLabel?: string;
  ctaHref?: string;
}

export function CtaBanner({
  title = "Need a custom fleet?",
  description = "Speak with our team about your department's requirements and procurement timeline.",
  ctaLabel = "Request Consultation",
  ctaHref = "/request-consultation",
}: CtaBannerProps) {
  return (
    <SlideUp>
      <div className="rounded-2xl bg-charcoal px-8 py-12 text-center md:px-16 md:py-16">
        <h2 className="text-2xl font-bold text-white md:text-3xl lg:text-4xl">{title}</h2>
        <p className="mx-auto mt-4 max-w-xl text-white/70">{description}</p>
        <Link
          href={ctaHref}
          className={cn(
            buttonVariants({ size: "lg" }),
            "mt-8 bg-accent-red text-white hover:bg-accent-red/90"
          )}
        >
          {ctaLabel}
        </Link>
      </div>
    </SlideUp>
  );
}
