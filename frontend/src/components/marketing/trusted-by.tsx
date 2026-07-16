import { trustedBy } from "@/content/site";
import { SlideUp } from "./motion";

export function TrustedBy() {
  return (
    <SlideUp>
      <div className="text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-steel">Trusted By</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
          {trustedBy.map((name) => (
            <span key={name} className="text-base font-semibold text-charcoal/70 md:text-lg">
              {name}
            </span>
          ))}
        </div>
      </div>
    </SlideUp>
  );
}
