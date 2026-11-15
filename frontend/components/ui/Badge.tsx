import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "destructive" | "warning" | "outline";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variants = {
    default: "bg-brand-950 text-brand-300 border-brand-800",
    success: "bg-emerald-950/80 text-emerald-300 border-emerald-800",
    destructive: "bg-red-950/80 text-red-300 border-red-800",
    warning: "bg-amber-950/80 text-amber-300 border-amber-800",
    outline: "text-slate-300 border-slate-700 bg-transparent",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
