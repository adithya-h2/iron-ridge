import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  label?: string;
  className?: string;
}

export function LoadingSpinner({ label = "Loading...", className }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center gap-2 text-muted-foreground", className)}>
      <Loader2 className="h-6 w-6 animate-spin" aria-hidden />
      <span className="text-sm">{label}</span>
    </div>
  );
}
