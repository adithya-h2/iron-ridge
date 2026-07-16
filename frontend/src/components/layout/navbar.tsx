"use client";

import Link from "next/link";
import { Menu } from "lucide-react";

import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { SidebarNav } from "@/components/layout/sidebar";
import { useAuth } from "@/hooks/use-auth";

export function Navbar() {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 lg:px-6">
      <Sheet>
        <SheetTrigger render={<Button variant="outline" size="icon" className="lg:hidden" />}>
          <Menu className="h-4 w-4" />
          <span className="sr-only">Open navigation</span>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SidebarNav />
        </SheetContent>
      </Sheet>

      <Link href="/app/dashboard" className="font-semibold tracking-tight">
        Iron Ridge
      </Link>

      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        <div className="hidden text-sm text-muted-foreground sm:block">
          {user?.email ?? "Guest"}
        </div>
      </div>
    </header>
  );
}
