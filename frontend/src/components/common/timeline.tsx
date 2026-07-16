import { cn } from "@/lib/utils";

export interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  timestamp?: string;
  status?: "completed" | "active" | "pending";
}

interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

export function Timeline({ items, className }: TimelineProps) {
  return (
    <ol className={cn("relative space-y-4 border-l border-border pl-6", className)}>
      {items.map((item) => (
        <li key={item.id} className="relative">
          <span
            className={cn(
              "absolute -left-[1.6rem] top-1 h-3 w-3 rounded-full border-2 bg-background",
              item.status === "completed" && "border-success bg-success",
              item.status === "active" && "border-accent bg-accent",
              item.status === "pending" && "border-muted-foreground"
            )}
          />
          <p className="font-medium">{item.title}</p>
          {item.description ? (
            <p className="text-sm text-muted-foreground">{item.description}</p>
          ) : null}
          {item.timestamp ? (
            <p className="text-xs text-muted-foreground">{item.timestamp}</p>
          ) : null}
        </li>
      ))}
    </ol>
  );
}
