"use client";

import { useState } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "@/components/ui/sonner";

import { AuthProvider } from "@/features/auth";
import { createQueryClient } from "@/lib/query-client";
import { ThemeProvider } from "@/components/theme-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => createQueryClient());

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {children}
          <Toaster richColors closeButton position="top-right" />
        </AuthProvider>
        {process.env.NODE_ENV === "development" && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
