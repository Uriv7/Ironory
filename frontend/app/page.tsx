"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/Table";
import {
  ScanEye,
  CheckCircle2,
  AlertOctagon,
  Clock,
  UploadCloud,
  Box,
  Cpu,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  FileText,
  Activity,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface OverviewMetrics {
  total_inspections: number;
  total_defective: number;
  total_passed: number;
  pass_rate_percentage: number;
  pending_reviews: number;
  avg_inference_time_ms: number;
  avg_confidence: number;
}

interface InspectionSummary {
  id: string;
  status: string;
  created_at: string;
  product_id: string;
  result?: {
    predicted_class: string;
    confidence: number;
    is_defective: boolean;
    inference_time_ms: number;
  };
  review?: {
    decision: string;
    final_class?: string;
  };
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<OverviewMetrics>({
    total_inspections: 0,
    total_defective: 0,
    total_passed: 0,
    pass_rate_percentage: 0.0,
    pending_reviews: 0,
    avg_inference_time_ms: 0.0,
    avg_confidence: 0.0,
  });
  const [inspections, setInspections] = useState<InspectionSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [overviewData, inspectionsData] = await Promise.allSettled([
          apiClient.get<OverviewMetrics>("/analytics/overview"),
          apiClient.get<InspectionSummary[]>("/inspections?limit=6"),
        ]);

        if (overviewData.status === "fulfilled") {
          setMetrics(overviewData.value);
        }
        if (inspectionsData.status === "fulfilled") {
          setInspections(inspectionsData.value);
        }
      } catch (err) {
        console.error("Failed to load dashboard telemetry:", err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Page Title & Operational Status */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white">
              Industrial Quality Inspection Overview
            </h2>
            <Badge variant="success" className="font-mono text-[10px]">
              AI Engine Online
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time visual defect detection and quality metrics for industrial manufacturing.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link href="/products/new">
            <Button variant="outline" size="sm" className="gap-1.5">
              <Box className="h-3.5 w-3.5 text-slate-400" />
              Register Product
            </Button>
          </Link>
          <Link href="/inspections">
            <Button variant="default" size="sm" className="gap-1.5">
              <UploadCloud className="h-3.5 w-3.5" />
              New Inspection
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Statistic Cards (Live Persisted DB Metrics) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Inspections */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Total Inspections
            </CardTitle>
            <ScanEye className="h-4 w-4 text-brand-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">
              {metrics.total_inspections}
            </div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Sessions</span> • {metrics.total_inspections} total runs recorded
            </p>
          </CardContent>
        </Card>

        {/* Quality Pass Rate */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Quality Pass Rate
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">
              {metrics.pass_rate_percentage}%
            </div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Passed</span> • {metrics.total_passed} non-defective units
            </p>
          </CardContent>
        </Card>

        {/* Detected Defects */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Detected Defects
            </CardTitle>
            <AlertOctagon className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">
              {metrics.total_defective}
            </div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Flagged</span> • Steel surface anomalies detected
            </p>
          </CardContent>
        </Card>

        {/* Pending Human Reviews */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Pending Quality Reviews
            </CardTitle>
            <Clock className="h-4 w-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">
              {metrics.pending_reviews}
            </div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Review Queue</span> • Awaiting supervisor sign-off
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Recent Inspections & Deep Learning Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left (2 cols): Persisted Inspection Records Table */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Inspection Stream</CardTitle>
                <CardDescription>
                  Audit log of recent automated vision inspections, predictions, and human reviews.
                </CardDescription>
              </div>
              <Link href="/inspections">
                <Button variant="ghost" size="sm" className="gap-1 text-xs text-brand-400">
                  View All <ArrowUpRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {inspections.length === 0 ? (
                <EmptyState
                  icon={<ScanEye className="w-8 h-8 text-slate-500" />}
                  title="No Quality Inspections Yet"
                  description="Upload a steel surface visual asset in the Inspections portal to run real-time AI classification and defect localization."
                  action={
                    <Link href="/inspections">
                      <Button variant="outline" size="sm" className="gap-2">
                        <UploadCloud className="h-3.5 w-3.5" />
                        Run First Inspection
                      </Button>
                    </Link>
                  }
                />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Inspection ID</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>AI Verdict</TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {inspections.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-mono text-xs font-semibold text-slate-200">
                          {item.id.slice(0, 8)}...
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              item.status === "COMPLETED"
                                ? "success"
                                : item.status === "REQUIRES_REVIEW"
                                ? "warning"
                                : item.status === "FAILED"
                                ? "destructive"
                                : "default"
                            }
                            className="text-[10px]"
                          >
                            {item.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs">
                          {item.result ? (
                            <span className="font-semibold text-slate-300">
                              {item.result.predicted_class.replace("_", " ").toUpperCase()}
                            </span>
                          ) : (
                            <span className="text-slate-500">In Processing</span>
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {item.result
                            ? `${(item.result.confidence * 100).toFixed(1)}%`
                            : "—"}
                        </TableCell>
                        <TableCell className="text-xs text-slate-400 font-mono">
                          {new Date(item.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </TableCell>
                        <TableCell className="text-right">
                          <Link href={`/inspections/${item.id}`}>
                            <Button variant="ghost" size="sm" className="text-xs text-brand-400">
                              View
                            </Button>
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right (1 col): AI Engine & Deep Learning Architecture Overview */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-brand-400" />
                AI Model Registry
              </CardTitle>
              <CardDescription>
                Trained deep learning models deployed for inference.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Baseline CNN */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    Baseline Custom CNN
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    NEU Steel Defect Classification
                  </div>
                </div>
                <Badge variant="success" className="text-[10px] font-mono">
                  Online &bull; Active
                </Badge>
              </div>

              {/* Transfer Learning */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    MobileNetV2 / EfficientNet
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    ImageNet Backbone + Fine-Tuning
                  </div>
                </div>
                <Badge variant="success" className="text-[10px] font-mono">
                  Online &bull; Active
                </Badge>
              </div>

              {/* Autoencoder */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    Convolutional Autoencoder
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    Unsupervised Anomaly Map
                  </div>
                </div>
                <Badge variant="default" className="text-[10px] font-mono">
                  Online &bull; Calibrated
                </Badge>
              </div>

              {/* U-Net Segmentation */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    U-Net Segmentation
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    Pixel-level Defect Localization
                  </div>
                </div>
                <Badge variant="default" className="text-[10px] font-mono">
                  Online &bull; Active
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Academic INT422 Streamlit Bridge */}
          <Card className="border-brand-900/50 bg-brand-950/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-semibold text-brand-300 flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5" />
                INT422 Academic Demonstration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                Interactive Streamlit application demonstrating dataset exploration, Grad-CAM explainability, model benchmarking, and DCGAN defect generation.
              </p>
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-brand-900/40">
                <span>Port: 8501</span>
                <span className="text-emerald-400 font-semibold">Available</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
