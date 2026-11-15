import * as React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle } from "lucide-react";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
  label?: string;
}

export function EmptyState({
  icon = <AlertCircle className="w-8 h-8 text-slate-500" />,
  title,
  description,
  action,
  className,
  label = "No Records Available",
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-slate-800 bg-slate-900/40 my-4",
        className
      )}
    >
      <div className="flex items-center justify-center w-14 h-14 rounded-full bg-slate-800/60 mb-4 border border-slate-700/60">
        {icon}
      </div>
      <span className="text-[10px] font-semibold tracking-wider text-brand-400 uppercase bg-brand-950/60 border border-brand-800/60 px-2 py-0.5 rounded-full mb-2">
        {label}
      </span>
      <h4 className="text-sm font-medium text-slate-200 mb-1">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm mb-5 leading-relaxed">
        {description}
      </p>
      {action && <div className="mt-1">{action}</div>}
    </div>
  );
}
