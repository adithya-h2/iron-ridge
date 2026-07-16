"use client";

import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";

interface SearchBoxProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export function SearchBox({
  placeholder = "Search...",
  value,
  onChange,
}: SearchBoxProps) {
  return (
    <div className="relative max-w-sm">
      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input
        className="pl-8"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
    </div>
  );
}
