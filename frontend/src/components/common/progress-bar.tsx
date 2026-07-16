import { Progress } from "@/components/ui/progress";

interface ProgressBarProps {
  value: number;
  label?: string;
}

export function ProgressBar({ value, label }: ProgressBarProps) {
  return (
    <div className="space-y-2">
      {label ? (
        <div className="flex justify-between text-sm">
          <span>{label}</span>
          <span className="text-muted-foreground">{Math.round(value)}%</span>
        </div>
      ) : null}
      <Progress value={value} />
    </div>
  );
}
