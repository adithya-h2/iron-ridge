import { Footer } from "@/components/layout/footer";
import { Navbar } from "@/components/layout/navbar";
import { SidebarNav } from "@/components/layout/sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden w-64 shrink-0 border-r bg-card lg:block">
        <div className="sticky top-0 flex h-screen flex-col">
          <SidebarNav />
        </div>
      </aside>
      <div className="flex min-h-screen flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-4 lg:p-6">{children}</main>
        <Footer />
      </div>
    </div>
  );
}
