"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";

import { navLinks } from "@/content/site";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

interface PublicNavbarProps {
  transparent?: boolean;
}

export function PublicNavbar({ transparent }: PublicNavbarProps) {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const useTransparent = transparent ?? isHome;
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isSolid = scrolled || !useTransparent;

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        isSolid
          ? "border-b border-border/60 bg-white/95 shadow-sm backdrop-blur-md"
          : "bg-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className={cn(
            "text-lg font-bold tracking-tight transition-colors",
            isSolid ? "text-charcoal" : "text-white"
          )}
        >
          Iron Ridge
        </Link>

        <nav className="hidden items-center gap-8 lg:flex" aria-label="Main navigation">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-accent-red",
                isSolid ? "text-steel" : "text-white/90 hover:text-white"
              )}
            >
              {label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <Link
            href="/request-consultation"
            className={cn(
              buttonVariants(),
              "bg-accent-red text-white hover:bg-accent-red/90"
            )}
          >
            Request Consultation
          </Link>
        </div>

        <button
          type="button"
          className={cn(
            "inline-flex items-center justify-center rounded-md p-2 lg:hidden",
            isSolid ? "text-charcoal" : "text-white"
          )}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {mobileOpen ? (
        <div className="border-t border-border bg-white lg:hidden">
          <nav className="flex flex-col gap-1 px-4 py-4" aria-label="Mobile navigation">
            {navLinks.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className="rounded-md px-3 py-2 text-sm font-medium text-charcoal hover:bg-muted"
                onClick={() => setMobileOpen(false)}
              >
                {label}
              </Link>
            ))}
            <Link
              href="/request-consultation"
              className={cn(buttonVariants(), "mt-2 bg-accent-red text-white hover:bg-accent-red/90")}
              onClick={() => setMobileOpen(false)}
            >
              Request Consultation
            </Link>
          </nav>
        </div>
      ) : null}
    </header>
  );
}
