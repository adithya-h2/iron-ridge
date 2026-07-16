import Link from "next/link";

import { PublicFooter, PublicNavbar } from "@/components/marketing";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function NotFound() {
  return (
    <>
      <PublicNavbar />
      <main className="flex flex-1 items-center justify-center px-4 py-32">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent-red">404</p>
          <h1 className="mt-4 text-4xl font-bold text-charcoal md:text-5xl">Page Not Found</h1>
          <p className="mx-auto mt-4 max-w-md text-steel">
            The page you are looking for does not exist or has been moved.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link href="/" className={cn(buttonVariants(), "bg-accent-red text-white hover:bg-accent-red/90")}>
              Go Home
            </Link>
            <Link href="/request-consultation" className={cn(buttonVariants({ variant: "outline" }))}>
              Request Consultation
            </Link>
          </div>
        </div>
      </main>
      <PublicFooter />
    </>
  );
}
