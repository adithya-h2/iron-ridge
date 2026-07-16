import { cn } from "@/lib/utils";

interface FeatureCardProps {
  title: string;
  description: string;
  className?: string;
}

export function FeatureCard({ title, description, className }: FeatureCardProps) {
  return (
    <article
      className={cn(
        "rounded-xl border border-border bg-white p-6 transition-shadow hover:shadow-md md:p-8",
        className
      )}
    >
      <h3 className="text-lg font-bold text-charcoal md:text-xl">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-steel md:text-base">{description}</p>
    </article>
  );
}
