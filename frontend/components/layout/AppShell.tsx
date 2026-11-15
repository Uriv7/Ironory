import * as React from "react";
import { Sidebar } from "./Sidebar";
import { TopNavbar } from "./TopNavbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <Sidebar />

      {/* Main View Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopNavbar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950/95">
          <div className="w-full max-w-[1920px] mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
