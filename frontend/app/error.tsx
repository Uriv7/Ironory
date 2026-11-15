"use client";

import * as React from "react";
import { Button } from "@/components/ui/Button";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    console.error("Application error boundary triggered:", error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] w-full flex-col items-center justify-center space-y-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-950/80 border border-red-800 text-red-400">
        <AlertTriangle className="h-7 w-7" />
      </div>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-slate-100">
          Inspection Interface Error
        </h2>
        <p className="text-xs text-slate-400 max-w-md">
          {error.message || "An unexpected error occurred while rendering the quality dashboard."}
        </p>
        {error.digest && (
          <p className="text-[10px] font-mono text-slate-500">
            Digest ID: {error.digest}
          </p>
        )}
      </div>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => reset()}
        className="gap-2"
      >
        <RefreshCw className="h-3.5 w-3.5" />
        Retry Operation
      </Button>
    </div>
  );
}
