import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="flex h-[60vh] w-full flex-col items-center justify-center space-y-3">
      <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      <div className="text-xs font-mono uppercase tracking-widest text-slate-400">
        Loading System State...
      </div>
    </div>
  );
}
