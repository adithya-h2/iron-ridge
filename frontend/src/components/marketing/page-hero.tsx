interface PageHeroProps {
  title: string;
  description?: string;
}

export function PageHero({ title, description }: PageHeroProps) {
  return (
    <div className="border-b border-border bg-muted/30 pt-24 pb-12 md:pt-28 md:pb-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold tracking-tight text-charcoal md:text-4xl lg:text-5xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-4 max-w-2xl text-lg text-steel">{description}</p>
        ) : null}
      </div>
    </div>
  );
}
