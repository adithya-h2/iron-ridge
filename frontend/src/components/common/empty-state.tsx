import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
}

export function EmptyState({
  title = "No data yet",
  description = "Content will appear here once this module is implemented.",
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-12 text-center">
      <Inbox className="h-10 w-10 text-muted-foreground" />
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
