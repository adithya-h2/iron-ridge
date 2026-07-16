import { cn } from "@/lib/utils";
import { Container } from "./container";

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  id?: string;
  variant?: "default" | "muted" | "dark";
}

const variantStyles = {
  default: "bg-background",
  muted: "bg-muted/50",
  dark: "bg-charcoal text-white",
};

export function Section({
  children,
  className,
  containerClassName,
  id,
  variant = "default",
}: SectionProps) {
  return (
    <section id={id} className={cn("py-16 md:py-24", variantStyles[variant], className)}>
      <Container className={containerClassName}>{children}</Container>
    </section>
  );
}
