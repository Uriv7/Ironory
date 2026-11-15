import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { FileQuestion, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] w-full flex-col items-center justify-center space-y-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-900 border border-slate-800 text-slate-400">
        <FileQuestion className="h-7 w-7" />
      </div>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-slate-100">
          Resource Not Found
        </h2>
        <p className="text-xs text-slate-400 max-w-sm">
          The requested inspection record, product, or dashboard view could not be located.
        </p>
      </div>
      <Link href="/">
        <Button variant="outline" size="sm" className="gap-2">
          <ArrowLeft className="h-3.5 w-3.5" />
          Return to Dashboard
        </Button>
      </Link>
    </div>
  );
}
