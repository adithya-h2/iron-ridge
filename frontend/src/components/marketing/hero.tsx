import Image from "next/image";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface HeroProps {
  headline: string;
  subheading: string;
  image: string;
  imageAlt?: string;
}

export function Hero({ headline, subheading, image, imageAlt = "Emergency response vehicle" }: HeroProps) {
  const lines = headline.split(". ").filter(Boolean);

  return (
    <section className="relative flex min-h-[85vh] items-end overflow-hidden">
      <Image
        src={image}
        alt={imageAlt}
        fill
        priority
        sizes="100vw"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-charcoal/90 via-charcoal/50 to-charcoal/30" />

      <div className="relative z-10 w-full pb-16 pt-32 md:pb-24 md:pt-40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl md:text-6xl lg:text-7xl">
            {lines.map((line, i) => (
              <span key={line} className="block">
                {line}{i < lines.length - 1 ? "." : ""}
              </span>
            ))}
          </h1>
          <p className="mt-6 max-w-xl text-lg text-white/85 md:text-xl">{subheading}</p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/request-consultation"
              className={cn(buttonVariants({ size: "lg" }), "bg-accent-red text-white hover:bg-accent-red/90")}
            >
              Request Consultation
            </Link>
            <Link
              href="/products"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "border-white/40 bg-white/10 text-white backdrop-blur-sm hover:bg-white/20"
              )}
            >
              Browse Vehicles
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
