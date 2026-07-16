import Image from "next/image";

import { cn } from "@/lib/utils";
import type { Industry } from "@/content/industries";

interface IndustryCardProps {
  industry: Industry;
  className?: string;
}

export function IndustryCard({ industry, className }: IndustryCardProps) {
  return (
    <article
      id={industry.id}
      className={cn(
        "group overflow-hidden rounded-xl border border-border bg-white transition-shadow hover:shadow-lg",
        className
      )}
    >
      <div className="relative aspect-[16/10] overflow-hidden">
        <Image
          src={industry.image}
          alt={industry.name}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
        />
      </div>
      <div className="p-6">
        <h3 className="text-xl font-bold text-charcoal">{industry.name}</h3>
        <p className="mt-2 text-sm leading-relaxed text-steel">{industry.description}</p>
        <ul className="mt-4 space-y-1">
          {industry.highlights.map((item) => (
            <li key={item} className="flex items-start gap-2 text-sm text-charcoal">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent-red" aria-hidden />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
}
