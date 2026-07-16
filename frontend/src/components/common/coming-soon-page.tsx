import { Construction } from "lucide-react";

import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent } from "@/components/ui/card";

interface ComingSoonPageProps {
  title: string;
  description?: string;
}

export function ComingSoonPage({ title, description }: ComingSoonPageProps) {
  return (
    <div>
      <PageHeader title={title} description={description} />
      <Card>
        <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
          <Construction className="h-12 w-12 text-muted-foreground" />
          <div>
            <p className="text-lg font-semibold">{title} — Coming Soon</p>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              This module is part of the Iron Ridge foundation. Business UI will be implemented in
              upcoming modules.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
