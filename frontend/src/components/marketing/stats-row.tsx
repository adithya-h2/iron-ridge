import { SlideUp } from "./motion";

interface Stat {
  label: string;
  value: string;
}

interface StatsRowProps {
  stats: readonly Stat[];
}

export function StatsRow({ stats }: StatsRowProps) {
  return (
    <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
      {stats.map((stat, index) => (
        <SlideUp key={stat.label} delay={index * 0.08}>
          <div className="text-center">
            <p className="text-3xl font-bold text-charcoal md:text-4xl lg:text-5xl">{stat.value}</p>
            <p className="mt-2 text-sm font-medium text-steel">{stat.label}</p>
          </div>
        </SlideUp>
      ))}
    </div>
  );
}
