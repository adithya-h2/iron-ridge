import Image from "next/image";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { VehicleCategory } from "@/content/vehicles";

interface VehicleCardProps {
  vehicle: VehicleCategory;
  variant?: "compact" | "full";
  className?: string;
}

export function VehicleCard({ vehicle, variant = "compact", className }: VehicleCardProps) {
  return (
    <article
      id={vehicle.id}
      className={cn(
        "group overflow-hidden rounded-xl border border-border bg-white transition-shadow hover:shadow-lg",
        className
      )}
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <Image
          src={vehicle.image}
          alt={vehicle.name}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
        />
      </div>
      <div className="p-6">
        <h3 className="text-xl font-bold text-charcoal">{vehicle.name}</h3>
        <p className="mt-2 text-sm leading-relaxed text-steel">{vehicle.description}</p>

        {variant === "full" ? (
          <>
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-steel">Specifications</p>
              <ul className="mt-2 space-y-1">
                {vehicle.specs.map((spec) => (
                  <li key={spec} className="text-sm text-charcoal">
                    {spec}
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-steel">Features</p>
              <ul className="mt-2 space-y-1">
                {vehicle.features.map((feature) => (
                  <li key={feature} className="text-sm text-charcoal">
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </>
        ) : null}

        <Link
          href={`/request-consultation?vehicle=${encodeURIComponent(vehicle.name)}`}
          className={cn(
            buttonVariants({ variant: variant === "full" ? "default" : "outline" }),
            "mt-6",
            variant === "full" && "bg-accent-red text-white hover:bg-accent-red/90"
          )}
        >
          {variant === "full" ? "Request Quote" : "Learn More"}
        </Link>
      </div>
    </article>
  );
}
