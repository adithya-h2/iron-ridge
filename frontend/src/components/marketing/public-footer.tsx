import Link from "next/link";

import { contactInfo, footerColumns } from "@/content/site";
import { Container } from "./container";

export function PublicFooter() {
  return (
    <footer className="border-t border-border bg-charcoal text-white">
      <Container className="py-16">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-1">
            <p className="text-lg font-bold">Iron Ridge</p>
            <p className="mt-3 text-sm text-white/70">
              American manufacturer of emergency response vehicles for fire, EMS, and municipal
              fleets.
            </p>
            <a
              href={contactInfo.linkedIn}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block text-sm text-white/70 hover:text-white"
              aria-label="Iron Ridge on LinkedIn"
            >
              LinkedIn
            </a>
          </div>

          <FooterColumn title="Products" links={footerColumns.products} />
          <FooterColumn title="Industries" links={footerColumns.industries} />
          <FooterColumn title="Resources" links={footerColumns.resources} />
          <FooterColumn title="Support" links={footerColumns.support} />
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-white/10 pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-white/60">
            &copy; {new Date().getFullYear()} Iron Ridge. All rights reserved.
          </p>
          <div className="flex gap-6">
            {footerColumns.legal.map(({ href, label }) => (
              <Link key={href} href={href} className="text-sm text-white/60 hover:text-white">
                {label}
              </Link>
            ))}
          </div>
        </div>
      </Container>
    </footer>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: readonly { href: string; label: string }[];
}) {
  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-wider text-white/90">{title}</p>
      <ul className="mt-4 space-y-2">
        {links.map(({ href, label }) => (
          <li key={href}>
            <Link href={href} className="text-sm text-white/60 transition-colors hover:text-white">
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
