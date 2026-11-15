"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import {
  ScanEye,
  ArrowLeft,
  CheckCircle2,
  AlertOctagon,
  Clock,
  ShieldCheck,
  FileCheck,
  Cpu,
  Save,
  AlertCircle,
  Hash,
} from "lucide-react";

interface InspectionDetail {
  id: string;
  organization_id: string;
  product_id: string;
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "REQUIRES_REVIEW" | "FAILED";
  error_message: string | null;
  created_at: string;
  image: {
    storage_key: string;
    original_filename: string;
    width: number;
    height: number;
    mime_type: string;
    file_size_bytes: number;
    checksum_sha256: string;
  } | null;
  result: {
    model_name: string;
    model_version: string;
    predicted_class: string;
    confidence: number;
    is_defective: boolean;
    anomaly_score: number | null;
    inference_time_ms: number;
    defects: Array<{
      id: string;
      defect_type: string;
      severity: string;
      confidence: number | null;
    }>;
  } | null;
  review: {
    decision: "CONFIRMED" | "OVERRIDDEN";
    final_class: string;
    is_defective: boolean;
    notes: string | null;
    created_at: string;
  } | null;
}

export default function InspectionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const inspectionId = params.id as string;

  const [inspection, setInspection] = React.useState<InspectionDetail | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  // Human Review Form state
  const [decision, setDecision] = React.useState<"CONFIRMED" | "OVERRIDDEN">("CONFIRMED");
  const [finalClass, setFinalClass] = React.useState("crazing");
  const [isDefective, setIsDefective] = React.useState(true);
  const [reviewNotes, setReviewNotes] = React.useState("");
  const [isSubmittingReview, setIsSubmittingReview] = React.useState(false);
  const [reviewFeedback, setReviewFeedback] = React.useState<string | null>(null);

  const fetchInspection = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const data = await apiClient.get<InspectionDetail>(`/inspections/${inspectionId}`, { headers });
      setInspection(data);

      if (data.result) {
        setFinalClass(data.result.predicted_class);
        setIsDefective(data.result.is_defective);
      }
      if (data.review) {
        setDecision(data.review.decision);
        setFinalClass(data.review.final_class);
        setIsDefective(data.review.is_defective);
        setReviewNotes(data.review.notes || "");
      }
    } catch (err) {
      if (err instanceof ApiException) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Unable to fetch inspection session details.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    if (inspectionId) {
      fetchInspection();
    }
  }, [inspectionId]);

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingReview(true);
    setReviewFeedback(null);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const updated = await apiClient.post<InspectionDetail>(
        `/inspections/${inspectionId}/review`,
        {
          decision,
          final_class: finalClass,
          is_defective: isDefective,
          notes: reviewNotes || null,
        },
        { headers }
      );

      setInspection(updated);
      setReviewFeedback("Human quality review signed off and persisted successfully.");
    } catch (err) {
      if (err instanceof ApiException) {
        setReviewFeedback(`Error: ${err.message}`);
      } else {
        setReviewFeedback("Review submission failed. Ensure Quality Manager privileges.");
      }
    } finally {
      setIsSubmittingReview(false);
    }
  };

  const imageUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/inspections/${inspectionId}/image`;

  return (
    <div className="space-y-6">
      {/* Navigation Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <Link href="/inspections">
            <Button variant="outline" size="sm" className="h-8 w-8 p-0">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                Inspection Session <span className="font-mono text-brand-400">#{inspectionId.slice(0, 8)}</span>
              </h2>
              {inspection && (
                <Badge
                  variant={
                    inspection.status === "COMPLETED"
                      ? "success"
                      : inspection.status === "REQUIRES_REVIEW"
                      ? "warning"
                      : "default"
                  }
                  className="font-mono text-[10px]"
                >
                  {inspection.status.replace("_", " ")}
                </Badge>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Logged: {inspection ? new Date(inspection.created_at).toLocaleString() : "Loading..."}
            </p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-md bg-red-950/70 border border-red-800 text-xs text-red-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Visual Asset Display */}
        <div className="space-y-4">
          <Card className="overflow-hidden">
            <CardHeader className="py-3 border-b border-slate-800">
              <CardTitle className="text-xs font-semibold flex items-center justify-between">
                <span>Original Surface Asset</span>
                <span className="font-mono text-[11px] text-slate-400">
                  {inspection?.image?.width} x {inspection?.image?.height} px
                </span>
              </CardTitle>
            </CardHeader>
            <div className="relative aspect-square w-full bg-slate-950 flex items-center justify-center p-2 border-b border-slate-800">
              {/* Image stream */}
              <img
                src={imageUrl}
                alt="Surface Inspection Asset"
                className="max-h-full max-w-full object-contain rounded border border-slate-800/80 shadow-md"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = "none";
                }}
              />
            </div>
            <CardContent className="pt-3 space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400">
                <div>
                  <span className="text-slate-500">Filename:</span> {inspection?.image?.original_filename}
                </div>
                <div>
                  <span className="text-slate-500">MIME:</span> {inspection?.image?.mime_type}
                </div>
                <div>
                  <span className="text-slate-500">Size:</span>{" "}
                  {inspection?.image ? Math.round(inspection.image.file_size_bytes / 1024) : 0} KB
                </div>
                <div>
                  <span className="text-slate-500">Storage:</span> Secure Local S3
                </div>
              </div>
              <div className="pt-2 border-t border-slate-800/60 text-[10px] font-mono text-slate-500 break-all">
                <Hash className="h-3 w-3 inline mr-1 text-slate-600" />
                SHA-256: {inspection?.image?.checksum_sha256}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: AI Inference & Human Review */}
        <div className="space-y-5">
          {/* AI Result Card */}
          <Card className="border-brand-900/60 bg-gradient-to-br from-slate-900 to-navy-950">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-xs font-semibold text-brand-300 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-brand-400" />
                Deep Learning Model Inference Output
              </CardTitle>
              <CardDescription>
                Automated surface defect categorization and confidence score.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              {inspection?.result ? (
                <>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div>
                      <div className="text-[11px] uppercase tracking-wider text-slate-400 font-mono">
                        Classification
                      </div>
                      <div
                        className={`text-lg font-bold font-mono ${
                          inspection.result.is_defective ? "text-red-400" : "text-emerald-400"
                        }`}
                      >
                        {inspection.result.predicted_class}
                      </div>
                    </div>

                    <Badge variant={inspection.result.is_defective ? "destructive" : "success"} className="text-xs">
                      {inspection.result.is_defective ? "DEFECTIVE PART" : "ACCEPTABLE / PASS"}
                    </Badge>
                  </div>

                  {/* Confidence Bar */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Model Decision Confidence</span>
                      <span className="font-mono font-bold text-slate-200">
                        {Math.round(inspection.result.confidence * 100)}%
                      </span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          inspection.result.confidence >= 0.8
                            ? "bg-brand-500"
                            : "bg-amber-500"
                        }`}
                        style={{ width: `${Math.round(inspection.result.confidence * 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Metadata grid */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
                    <div>
                      <span className="text-slate-500">Model:</span> {inspection.result.model_name}
                    </div>
                    <div>
                      <span className="text-slate-500">Version:</span> {inspection.result.model_version}
                    </div>
                    <div>
                      <span className="text-slate-500">Inference Latency:</span> {inspection.result.inference_time_ms} ms
                    </div>
                    <div>
                      <span className="text-slate-500">Pipeline:</span> Phase 4 Keras
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-6 text-center text-xs text-slate-400 font-mono">
                  <Clock className="h-6 w-6 text-amber-400 mx-auto mb-2 animate-pulse" />
                  Inference Session in Queue (Awaiting Model Pipeline Execution)
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quality Manager Sign-Off Card */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-xs font-semibold flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                Human Quality Supervisor Audit Sign-Off
              </CardTitle>
              <CardDescription>
                Confirm or override model predictions before final certificate issuance.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleReviewSubmit}>
              <CardContent className="space-y-4 pt-4">
                {reviewFeedback && (
                  <div className="p-3 rounded-md bg-slate-900 border border-brand-800 text-xs text-brand-300 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-400" />
                    <span>{reviewFeedback}</span>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-medium text-slate-300">Auditor Action</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
                      value={decision}
                      onChange={(e) => setDecision(e.target.value as "CONFIRMED" | "OVERRIDDEN")}
                    >
                      <option value="CONFIRMED">CONFIRM AI Result</option>
                      <option value="OVERRIDDEN">OVERRIDE AI Result</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-medium text-slate-300">Final Assigned Class</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
                      value={finalClass}
                      onChange={(e) => setFinalClass(e.target.value)}
                    >
                      <option value="healthy">healthy (No Defect / Pass)</option>
                      <option value="crazing">crazing (Micro-cracks)</option>
                      <option value="inclusion">inclusion (Foreign Matter)</option>
                      <option value="patches">patches (Surface Oxidation)</option>
                      <option value="pitted_surface">pitted_surface (Cavities)</option>
                      <option value="rolled-in_scale">rolled-in_scale (Mill Scale)</option>
                      <option value="scratches">scratches (Abrasion)</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300">Auditor Notes</label>
                  <textarea
                    rows={3}
                    className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    placeholder="Enter compliance verification notes, root-cause remarks, or reason for override..."
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-end gap-2 border-t border-slate-800">
                <Button
                  type="submit"
                  variant="default"
                  size="sm"
                  isLoading={isSubmittingReview}
                  className="gap-2"
                >
                  <Save className="h-4 w-4" />
                  Persist Audit Decision
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
