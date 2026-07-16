"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ClipboardCheck,
  LayoutDashboard,
  Package,
  Settings,
  Users,
  Workflow,
  Radar,
} from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/app/leads", label: "Leads", icon: Users },
  { href: "/app/workflow", label: "Workflow", icon: Workflow },
  { href: "/app/orders", label: "Orders", icon: Package },
  { href: "/app/approvals", label: "Approvals", icon: ClipboardCheck },
  { href: "/app/tracking", label: "Tracking", icon: Radar },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1 p-4">
      <div className="mb-4 px-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Iron Ridge
        </p>
        <p className="text-sm text-muted-foreground">Sales Workflow</p>
      </div>
      {navItems.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        );
      })}
      <div className="mt-auto pt-4">
        <Link
          href="/app/dashboard"
          className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
        >
          <BarChart3 className="h-4 w-4" />
          Analytics (Soon)
        </Link>
      </div>
    </nav>
  );
}
