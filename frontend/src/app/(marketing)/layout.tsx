import { PublicFooter, PublicNavbar } from "@/components/marketing";
import { createPageMetadata, siteConfig } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: siteConfig.name,
  description: siteConfig.description,
  path: "/",
});

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <PublicNavbar />
      <main className="flex-1">{children}</main>
      <PublicFooter />
    </>
  );
}
