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
  FileCheck,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Title & Operational Status */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white">
              Industrial Quality Inspection Overview
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              Phase 1: Foundation
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
          <Link href="/inspections/new">
            <Button variant="default" size="sm" className="gap-1.5">
              <UploadCloud className="h-3.5 w-3.5" />
              New Inspection
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Statistic Cards (Strict: Actual Zero/Empty Baseline, No Fake Numbers) */}
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
            <div className="text-2xl font-bold font-mono text-white">0</div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Baseline</span> • Zero runs recorded
            </p>
          </CardContent>
        </Card>

        {/* Successful / Passed */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Quality Pass Rate
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">0.0%</div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Passed</span> • 0 defective / 0 inspected
            </p>
          </CardContent>
        </Card>

        {/* Defective Units */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b-0">
            <CardTitle className="text-xs font-medium text-slate-400">
              Detected Defects
            </CardTitle>
            <AlertOctagon className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-white">0</div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Critical</span> • No surface defects flagged
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
            <div className="text-2xl font-bold font-mono text-white">0</div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
              <span className="text-slate-400">Review Queue</span> • All caught up
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
                  Audit log of recent automated vision inspections and human sign-offs.
                </CardDescription>
              </div>
              <Badge variant="outline" className="font-mono text-[10px]">
                Live Feed
              </Badge>
            </CardHeader>
            <CardContent>
              {/* Explicit Empty State */}
              <EmptyState
                icon={<ScanEye className="w-8 h-8 text-slate-500" />}
                title="No Quality Inspections Yet"
                description="Inspection sessions created in Phase 3 will appear here in real time with predicted defect classes, confidence scores, and human review decisions."
                action={
                  <Link href="/inspections/new">
                    <Button variant="outline" size="sm" className="gap-2">
                      <UploadCloud className="h-3.5 w-3.5" />
                      Configure Inspection Run
                    </Button>
                  </Link>
                }
              />
            </CardContent>
          </Card>
        </div>

        {/* Right (1 col): AI Engine & Deep Learning Architecture Overview */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-brand-400" />
                AI Model Architecture
              </CardTitle>
              <CardDescription>
                Deep learning models prepared for INT422 and industrial inspection.
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
                <Badge variant="warning" className="text-[10px] font-mono">
                  Phase 4 Training
                </Badge>
              </div>

              {/* Transfer Learning */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    MobileNetV2 / EfficientNet
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    ImageNet Pretrained + Fine-Tuning
                  </div>
                </div>
                <Badge variant="warning" className="text-[10px] font-mono">
                  Phase 4 Training
                </Badge>
              </div>

              {/* Autoencoder */}
              <div className="flex items-center justify-between p-3 rounded-md bg-slate-950/60 border border-slate-800">
                <div className="space-y-0.5">
                  <div className="text-xs font-semibold text-slate-200">
                    Convolutional Autoencoder
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    MVTec AD Anomaly Reconstruction
                  </div>
                </div>
                <Badge variant="outline" className="text-[10px] font-mono">
                  Phase 5 Autoencoder
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
                <Badge variant="outline" className="text-[10px] font-mono">
                  Phase 5 Segmentation
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
                A dedicated Streamlit application connects to identical model weights and preprocessing pipelines for interactive curriculum evaluation.
              </p>
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-brand-900/40">
                <span>Port: 8501</span>
                <span>Target: Phase 7</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
