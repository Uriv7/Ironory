"use client";

import * as React from "react";
import { apiClient } from "@/lib/api-client";
import { Bell, Activity, CheckCircle2, AlertTriangle, ShieldCheck, User } from "lucide-react";

interface HealthState {
  status: "online" | "offline" | "checking";
  latencyMs?: number;
  environment?: string;
}

export function TopNavbar() {
  const [health, setHealth] = React.useState<HealthState>({
    status: "checking",
  });

  React.useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      const startTime = performance.now();
      try {
        const data = await apiClient.get<{ status: string; environment: string }>("/health");
        const latency = Math.round(performance.now() - startTime);
        if (isMounted) {
          setHealth({
            status: data.status === "ok" ? "online" : "offline",
            latencyMs: latency,
            environment: data.environment,
          });
        }
      } catch {
        if (isMounted) {
          setHealth({ status: "offline" });
        }
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-slate-800 bg-navy-950/90 px-6 backdrop-blur-md">
      {/* Title & Context */}
      <div className="flex items-center space-x-3">
        <h1 className="text-sm font-semibold tracking-tight text-slate-100">
          Industrial Quality Inspection Operations
        </h1>
        <span className="hidden sm:inline-block text-slate-600">/</span>
        <span className="hidden sm:inline-block text-xs text-slate-400 font-mono">
          INT422 & Commercial SaaS
        </span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Live Backend Connection Status */}
        <div className="flex items-center space-x-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs">
          <Activity className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-slate-400">Backend API:</span>
          {health.status === "online" && (
            <span className="flex items-center gap-1 font-mono text-[11px] font-semibold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              ONLINE {health.latencyMs ? `(${health.latencyMs}ms)` : ""}
            </span>
          )}
          {health.status === "checking" && (
            <span className="font-mono text-[11px] text-amber-400">CONNECTING...</span>
          )}
          {health.status === "offline" && (
            <span className="flex items-center gap-1 font-mono text-[11px] font-semibold text-red-400">
              <span className="h-2 w-2 rounded-full bg-red-500"></span>
              OFFLINE
            </span>
          )}
        </div>

        {/* Notifications */}
        <button
          className="relative rounded-md p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          title="System Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-brand-500"></span>
        </button>

        {/* User Profile */}
        <div className="flex items-center space-x-2.5 border-l border-slate-800 pl-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            <User className="h-4 w-4" />
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-xs font-medium text-slate-200 leading-tight">
              Dr. Alex Miller
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              Quality Inspector (Org Owner)
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
