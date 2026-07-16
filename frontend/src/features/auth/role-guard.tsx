"use client";

import type { UserRole } from "@/types/auth";
import { useAuth } from "@/hooks/use-auth";

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({ allowedRoles, children, fallback = null }: RoleGuardProps) {
  const { user } = useAuth();
  if (!user) return fallback;
  if (!allowedRoles.includes(user.role as UserRole) && user.role !== "admin") {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}
