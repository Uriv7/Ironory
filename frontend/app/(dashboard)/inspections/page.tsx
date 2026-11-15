"use client";

import * as React from "react";
import Link from "next/link";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { ScanEye, UploadCloud, CheckCircle2, AlertOctagon, Clock, Eye, AlertCircle, RefreshCw, FileDown, Layers } from "lucide-react";

interface ProductOption {
  id: string;
  name: string;
  code: string;
}

interface InspectionItem {
  id: string;
  product_id: string;
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "REQUIRES_REVIEW" | "FAILED";
  error_message: string | null;
  created_at: string;
  image: {
    original_filename: string;
    width: number;
    height: number;
    mime_type: string;
    file_size_bytes: number;
  } | null;
  result: {
    predicted_class: string;
    confidence: number;
    is_defective: boolean;
    model_name: string;
  } | null;
  review: {
    decision: string;
    final_class: string;
    is_defective: boolean;
  } | null;
}

export default function InspectionsCenterPage() {
  const [products, setProducts] = React.useState<ProductOption[]>([]);
  const [selectedProductId, setSelectedProductId] = React.useState<string>("");
  const [file, setFile] = React.useState<File | null>(null);
  const [batchFiles, setBatchFiles] = React.useState<File[]>([]);
  const [isBatchMode, setIsBatchMode] = React.useState(false);
  const [isUploading, setIsUploading] = React.useState(false);
  const [uploadFeedback, setUploadFeedback] = React.useState<{ type: "success" | "error"; text: string } | null>(null);

  const [inspections, setInspections] = React.useState<InspectionItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState<string>("");

  const fetchInitialData = async () => {
    setIsLoading(true);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      // 1. Fetch Products
      const prods = await apiClient.get<ProductOption[]>("/products", { headers });
      setProducts(prods);
      if (prods.length > 0 && !selectedProductId) {
        setSelectedProductId(prods[0].id);
      }

      // 2. Fetch Inspections
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      const url = `/inspections${params.toString() ? `?${params.toString()}` : ""}`;
      const data = await apiClient.get<InspectionItem[]>(url, { headers });
      setInspections(data);
    } catch (err) {
      if (err instanceof ApiException) {
        setUploadFeedback({ type: "error", text: err.message });
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchInitialData();
  }, [statusFilter]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProductId) {
      setUploadFeedback({ type: "error", text: "Please select a product." });
      return;
    }

    if (isBatchMode) {
      if (batchFiles.length === 0) {
        setUploadFeedback({ type: "error", text: "Please select at least one image file for batch inspection." });
        return;
      }
      setIsUploading(true);
      setUploadFeedback(null);
      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
        const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

        const formData = new FormData();
        formData.append("product_id", selectedProductId);
        for (const f of batchFiles) {
          formData.append("files", f);
        }

        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;
        if (orgId) headers["X-Organization-ID"] = orgId;

        const res = await apiClient.post<{ batch_size: number; successful_count: number; failed_count: number }>(
          "/inspections/batch",
          formData,
          { headers }
        );
        setUploadFeedback({
          type: "success",
          text: `Batch processing complete: ${res.successful_count} of ${res.batch_size} inspections created successfully.`,
        });
        setBatchFiles([]);
        fetchInitialData();
      } catch (err) {
        if (err instanceof ApiException) {
          setUploadFeedback({ type: "error", text: err.message });
        } else {
          setUploadFeedback({ type: "error", text: "Batch upload failed. Verify files and permissions." });
        }
      } finally {
        setIsUploading(false);
      }
    } else {
      if (!file) {
        setUploadFeedback({ type: "error", text: "Please select an image file." });
        return;
      }

      setIsUploading(true);
      setUploadFeedback(null);

      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
        const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

        const formData = new FormData();
        formData.append("product_id", selectedProductId);
        formData.append("file", file);

        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;
        if (orgId) headers["X-Organization-ID"] = orgId;

        const newInsp = await apiClient.post<InspectionItem>("/inspections/upload", formData, { headers });
        setUploadFeedback({
          type: "success",
          text: `Inspection session #${newInsp.id.slice(0, 8)} queued successfully.`,
        });
        setFile(null);
        fetchInitialData();
      } catch (err) {
        if (err instanceof ApiException) {
          setUploadFeedback({ type: "error", text: err.message });
        } else {
          setUploadFeedback({ type: "error", text: "Upload failed. Verify image format and tenant permissions." });
        }
      } finally {
        setIsUploading(false);
      }
    }
  };

  const handleExportCsv = () => {
    const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const exportUrl = `${apiUrl}/inspections/export/csv${selectedProductId ? `?product_id=${selectedProductId}` : ""}`;
    window.open(exportUrl, "_blank");
  };

  const getStatusBadgeVariant = (status: InspectionItem["status"]) => {
    switch (status) {
      case "COMPLETED":
        return "success";
      case "REQUIRES_REVIEW":
        return "warning";
      case "FAILED":
        return "destructive";
      default:
        return "default";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <ScanEye className="h-5 w-5 text-brand-400" />
              Live Visual Inspection Center
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              Session Engine
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Submit high-resolution surface captures for deep learning classification and quality verification.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start">
          <Button variant="outline" size="sm" onClick={handleExportCsv} className="gap-1.5">
            <FileDown className="h-3.5 w-3.5 text-brand-400" />
            Export Audit CSV
          </Button>
          <Button variant="outline" size="sm" onClick={fetchInitialData} className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh Stream
          </Button>
        </div>
      </div>

      {/* Upload Zone Card */}
      <Card className="border-brand-900/50 bg-gradient-to-r from-slate-900 via-navy-950 to-slate-900">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sm flex items-center gap-2">
              <UploadCloud className="h-4 w-4 text-brand-400" />
              {isBatchMode ? "Batch Surface Ingestion (Up to 20 Frames)" : "Ingest Single Surface Asset"}
            </CardTitle>
            <CardDescription>
              Supported: JPEG, PNG, WEBP (min 32x32, max 4096x4096). Stored in encrypted tenant storage.
            </CardDescription>
          </div>
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-md border border-slate-800">
            <button
              type="button"
              onClick={() => { setIsBatchMode(false); setUploadFeedback(null); }}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                !isBatchMode ? "bg-brand-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Single Frame
            </button>
            <button
              type="button"
              onClick={() => { setIsBatchMode(true); setUploadFeedback(null); }}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors flex items-center gap-1 ${
                isBatchMode ? "bg-brand-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Layers className="h-3 w-3" />
              Batch Ingest
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {uploadFeedback && (
            <div
              className={`p-3 mb-4 rounded-md text-xs flex items-center gap-2 ${
                uploadFeedback.type === "success"
                  ? "bg-emerald-950/70 border border-emerald-800 text-emerald-300"
                  : "bg-red-950/70 border border-red-800 text-red-300"
              }`}
            >
              {uploadFeedback.type === "success" ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-400" />
              )}
              <span>{uploadFeedback.text}</span>
            </div>
          )}

          <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* Product Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300">Target Product</label>
              <select
                className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 transition-colors focus:outline-none focus:ring-1 focus:ring-brand-500"
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                disabled={products.length === 0}
              >
                {products.length === 0 && <option value="">No products registered yet</option>}
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.code})
                  </option>
                ))}
              </select>
            </div>

            {/* File Input */}
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300">
                {isBatchMode ? `Surface Image Files (${batchFiles.length} selected)` : "Surface Image File"}
              </label>
              {isBatchMode ? (
                <input
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setBatchFiles(Array.from(e.target.files || []).slice(0, 20))}
                  className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-300 file:mr-2 file:rounded file:border-0 file:bg-slate-800 file:px-2 file:py-0.5 file:text-xs file:text-slate-200 cursor-pointer"
                />
              ) : (
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-300 file:mr-2 file:rounded file:border-0 file:bg-slate-800 file:px-2 file:py-0.5 file:text-xs file:text-slate-200 cursor-pointer"
                />
              )}
            </div>

            {/* Action */}
            <Button
              type="submit"
              variant="default"
              size="md"
              isLoading={isUploading}
              disabled={isBatchMode ? batchFiles.length === 0 || !selectedProductId : !file || !selectedProductId}
              className="gap-2 h-9"
            >
              <UploadCloud className="h-4 w-4" />
              {isBatchMode ? `Process Batch (${batchFiles.length})` : "Upload & Run Inspection"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Filter and Session Feed Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle>Inspection Sessions Stream</CardTitle>
            <CardDescription>
              Chronological log of automated vision runs, confidence gating, and human reviews.
            </CardDescription>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Status:</span>
            <select
              className="h-8 rounded-md border border-slate-700 bg-slate-900 px-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="QUEUED">Queued</option>
              <option value="PROCESSING">Processing</option>
              <option value="COMPLETED">Completed</option>
              <option value="REQUIRES_REVIEW">Requires Review</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {inspections.length === 0 && !isLoading && (
            <EmptyState
              icon={<ScanEye className="w-8 h-8 text-slate-500" />}
              title="No Inspection Sessions Found"
              description="Upload a surface defect image above to initiate your first quality inspection session."
            />
          )}

          {inspections.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Inspection ID</TableHead>
                  <TableHead>Image Metadata</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>AI Defect Prediction</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {inspections.map((insp) => (
                  <TableRow key={insp.id}>
                    <TableCell className="font-mono text-xs text-slate-200">
                      {insp.id.slice(0, 8)}...
                    </TableCell>
                    <TableCell>
                      <div className="text-slate-300 font-sans text-xs">
                        {insp.image?.original_filename || "Asset"}
                      </div>
                      {insp.image && (
                        <div className="text-[10px] text-slate-500 font-mono">
                          {insp.image.width}x{insp.image.height} • {Math.round(insp.image.file_size_bytes / 1024)} KB
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadgeVariant(insp.status)} className="font-mono text-[10px]">
                        {insp.status.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {insp.result ? (
                        <span className={`font-mono text-xs font-semibold ${
                          insp.result.is_defective ? "text-red-400" : "text-emerald-400"
                        }`}>
                          {insp.result.predicted_class}
                        </span>
                      ) : (
                        <span className="text-slate-500 text-xs font-mono">Awaiting Inference</span>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-slate-300">
                      {insp.result ? `${Math.round(insp.result.confidence * 100)}%` : "-"}
                    </TableCell>
                    <TableCell className="text-slate-500 text-xs">
                      {new Date(insp.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Link href={`/inspections/${insp.id}`}>
                        <Button variant="outline" size="sm" className="h-7 text-[11px] gap-1">
                          <Eye className="h-3 w-3" />
                          Inspect
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
  );
}
