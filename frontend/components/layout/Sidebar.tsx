"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Box,
  ScanEye,
  BarChart3,
  FileText,
  Users,
  Settings,
  ShieldAlert,
  Cpu,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  { title: "Inspection Dashboard", href: "/", icon: LayoutDashboard },
  { title: "Products & Parts", href: "/products", icon: Box },
  { title: "Live Inspection Center", href: "/inspections", icon: ScanEye },
  { title: "Quality Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Audit & PDF Reports", href: "/reports", icon: FileText },
  { title: "Team & Permissions", href: "/team", icon: Users },
  { title: "AI Model Registry", href: "/models", icon: Cpu, badge: "DL" },
  { title: "Organization Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-800 bg-navy-950 text-slate-300 transition-all duration-200 select-none",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/80">
        {!collapsed && (
          <Link href="/" className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-sm">
              <ScanEye className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-sm tracking-tight text-white flex items-center gap-1.5">
                Ironory <span className="text-[10px] text-brand-400 font-mono font-bold bg-brand-950 border border-brand-800 px-1 py-0.2 rounded">AI</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono tracking-wider uppercase">Industrial SaaS</span>
            </div>
          </Link>
        )}
        {collapsed && (
          <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
            <ScanEye className="h-5 w-5" />
          </div>
        )}
      </div>

      {/* Tenant Indicator */}
      {!collapsed ? (
        <div className="px-4 py-3 border-b border-slate-800/60 bg-slate-900/40">
          <div className="text-[10px] uppercase font-mono tracking-wider text-slate-500 mb-1">
            Active Tenant
          </div>
          <div className="flex items-center justify-between text-xs font-medium text-slate-200">
            <span className="truncate">Acme Steel Corp</span>
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">Org ID: org-prod-001</span>
        </div>
      ) : (
        <div className="py-2 border-b border-slate-800/60 flex justify-center">
          <div className="h-2 w-2 rounded-full bg-emerald-400" title="Acme Steel Corp (Online)" />
        </div>
      )}

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center rounded-md px-3 py-2 text-xs font-medium transition-colors group",
                isActive
                  ? "bg-brand-900/60 text-brand-300 border-l-2 border-brand-500 font-semibold"
                  : "text-slate-400 hover:bg-slate-900/80 hover:text-slate-200"
              )}
              title={collapsed ? item.title : undefined}
            >
              <Icon
                className={cn(
                  "h-4 w-4 shrink-0 transition-colors",
                  isActive ? "text-brand-400" : "text-slate-500 group-hover:text-slate-300",
                  !collapsed && "mr-3"
                )}
              />
              {!collapsed && (
                <span className="flex-1 truncate">{item.title}</span>
              )}
              {!collapsed && item.badge && (
                <span className="ml-auto rounded bg-slate-800 px-1.5 py-0.5 text-[9px] font-mono text-slate-400">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-2 border-t border-slate-800/80 flex items-center justify-between">
        {!collapsed && (
          <div className="text-[11px] text-slate-500 font-mono px-2">v1.0.0 (Phase 1)</div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors ml-auto"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
