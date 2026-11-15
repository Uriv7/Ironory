import * as React from "react";
import Link from "next/link";
import { ScanEye } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen w-full flex-col justify-center items-center bg-slate-950 px-4 py-12 sm:px-6 lg:px-8">
      {/* Brand Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-8">
        <Link href="/" className="inline-flex items-center space-x-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 text-white shadow-lg shadow-brand-500/20">
            <ScanEye className="h-6 w-6" />
          </div>
          <span className="font-bold text-2xl tracking-tight text-white flex items-center gap-2">
            Ironory <span className="text-xs text-brand-400 font-mono font-bold bg-brand-950 border border-brand-800 px-1.5 py-0.5 rounded">AI</span>
          </span>
        </Link>
        <p className="mt-2 text-xs font-mono uppercase tracking-widest text-slate-400">
          Industrial Quality Inspection SaaS
        </p>
      </div>

      {/* Main Content Box */}
      <div className="w-full sm:max-w-md">{children}</div>

      {/* Footer */}
      <div className="mt-8 text-center text-xs text-slate-500 font-mono">
        Ironory SaaS • INT422 Deep Learning Project
      </div>
    </div>
  );
}
