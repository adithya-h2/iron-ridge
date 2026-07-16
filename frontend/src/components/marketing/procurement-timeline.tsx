import type { ProcessStep } from "@/content/process-steps";
import { SlideUp } from "./motion";

interface ProcurementTimelineProps {
  steps: ProcessStep[];
  variant?: "horizontal" | "vertical";
}

export function ProcurementTimeline({ steps, variant = "horizontal" }: ProcurementTimelineProps) {
  if (variant === "vertical") {
    return (
      <div className="space-y-0">
        {steps.map((step, index) => (
          <SlideUp key={step.id} delay={index * 0.05}>
            <div className="relative flex gap-6 pb-10 last:pb-0">
              {index < steps.length - 1 ? (
                <div className="absolute left-[15px] top-8 h-full w-px bg-border" aria-hidden />
              ) : null}
              <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-red text-sm font-bold text-white">
                {index + 1}
              </div>
              <div className="pt-0.5">
                <h3 className="text-lg font-bold text-charcoal">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-steel">{step.description}</p>
              </div>
            </div>
          </SlideUp>
        ))}
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute left-0 right-0 top-6 hidden h-px bg-border md:block" aria-hidden />
      <ol className="grid gap-8 md:grid-cols-7">
        {steps.map((step, index) => (
          <SlideUp key={step.id} delay={index * 0.05}>
            <li className="relative text-center">
              <div className="relative z-10 mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-accent-red text-sm font-bold text-white">
                {index + 1}
              </div>
              <h3 className="mt-4 text-sm font-bold text-charcoal">{step.title}</h3>
              <p className="mt-2 hidden text-xs leading-relaxed text-steel lg:block">
                {step.description}
              </p>
            </li>
          </SlideUp>
        ))}
      </ol>
    </div>
  );
}
