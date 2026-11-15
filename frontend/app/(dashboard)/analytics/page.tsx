"use client";

import * as React from "react";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { BarChart3, TrendingUp, AlertTriangle, ShieldCheck, RefreshCw, Layers } from "lucide-react";

interface AnalyticsOverview {
  total_inspections: number;
  pass_rate_percentage: number;
  defective_count: number;
  requires_review_count: number;
  recent_24h_count: number;
}

interface DefectClassMetric {
  defect_type: string;
  count: number;
  percentage: number;
}

interface TrendDay {
  date: string;
  total_inspections: number;
  defective_inspections: number;
  pass_rate_percentage: number;
}

export default function AnalyticsPage() {
  const [overview, setOverview] = React.useState<AnalyticsOverview | null>(null);
  const [defects, setDefects] = React.useState<DefectClassMetric[]>([]);
  const [trends, setTrends] = React.useState<TrendDay[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const [ovData, defData, trData] = await Promise.all([
        apiClient.get<AnalyticsOverview>("/analytics/overview", { headers }),
        apiClient.get<DefectClassMetric[]>("/analytics/defect-distribution", { headers }),
        apiClient.get<TrendDay[]>("/analytics/trends", { headers }),
      ]);

      setOverview(ovData);
      setDefects(defData);
      setTrends(trData);
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.message);
      } else {
        setError("Unable to retrieve quality analytics telemetry.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-brand-400" />
              Industrial Quality Analytics & Telemetry
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              ISO 9001 Telemetry
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Statistical process control, Pareto defect breakdown, and shift quality yield tracking.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={fetchAnalytics} isLoading={isLoading} className="gap-1.5 self-start">
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh Metrics
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-md bg-amber-950/60 border border-amber-800 text-amber-300 text-xs flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Total Inspections</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {overview?.total_inspections ?? 0}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-brand-950/70 border border-brand-800 flex items-center justify-center text-brand-400">
                <Layers className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Quality Yield / Pass Rate</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1">
                  {overview ? `${overview.pass_rate_percentage.toFixed(1)}%` : "0.0%"}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-emerald-950/70 border border-emerald-800 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Surface Defects Detected</p>
                <p className="text-2xl font-bold text-red-400 mt-1">
                  {overview?.defective_count ?? 0}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-red-950/70 border border-red-800 flex items-center justify-center text-red-400">
                <AlertTriangle className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400">Review Queue Items</p>
                <p className="text-2xl font-bold text-amber-400 mt-1">
                  {overview?.requires_review_count ?? 0}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-amber-950/70 border border-amber-800 flex items-center justify-center text-amber-400">
                <TrendingUp className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pareto Distribution & Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pareto Defect Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Defect Classification Pareto Distribution</CardTitle>
            <CardDescription>
              Multiclass frequency distribution of surface defects identified by deployed neural models.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {defects.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No surface defects logged yet. All inspected steel surfaces conform to nominal quality specifications.
              </div>
            ) : (
              <div className="space-y-3">
                {defects.map((d) => (
                  <div key={d.defect_type} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-200 capitalize">
                        {d.defect_type.replace(/_/g, " ")}
                      </span>
                      <span className="text-slate-400 font-mono">
                        {d.count} ({d.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-brand-500 to-amber-500 rounded-full"
                        style={{ width: `${Math.min(100, d.percentage)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 7-Day Shift Quality Trend */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Shift Quality Yield Trends (Rolling 7-Days)</CardTitle>
            <CardDescription>
              Inspection throughput and daily pass rates across active production shifts.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {trends.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                Awaiting production inspection sessions to build trend telemetry.
              </div>
            ) : (
              <div className="space-y-3">
                {trends.map((t) => (
                  <div
                    key={t.date}
                    className="flex items-center justify-between p-2 rounded-md bg-slate-950 border border-slate-800 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-slate-400">{t.date}</span>
                      <span className="text-slate-300">
                        {t.total_inspections} frame{t.total_inspections !== 1 ? "s" : ""}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-red-400 font-medium">
                        {t.defective_inspections} defect{t.defective_inspections !== 1 ? "s" : ""}
                      </span>
                      <Badge
                        variant={t.pass_rate_percentage >= 90 ? "success" : "warning"}
                        className="font-mono text-[11px]"
                      >
                        {t.pass_rate_percentage.toFixed(1)}% Yield
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
