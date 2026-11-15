"use client";

import * as React from "react";
import Link from "next/link";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { FileText, FileDown, RefreshCw, Eye, ShieldCheck, AlertCircle } from "lucide-react";

interface InspectionReportItem {
  id: string;
  product_id: string;
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "REQUIRES_REVIEW" | "FAILED";
  created_at: string;
  image: {
    original_filename: string;
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

export default function ReportsPage() {
  const [reports, setReports] = React.useState<InspectionReportItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const fetchReports = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const data = await apiClient.get<InspectionReportItem[]>("/inspections?limit=50", { headers });
      setReports(data);
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.message);
      } else {
        setError("Failed to load inspection certificates.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchReports();
  }, []);

  const handleExportCsv = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    window.open(`${apiUrl}/inspections/export/csv`, "_blank");
  };

  const getPdfUrl = (id: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    return `${apiUrl}/inspections/${id}/report.pdf`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <FileText className="h-5 w-5 text-brand-400" />
              Audit Certificates & ISO 9001 PDF Reports
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              Compliance Engine
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Download individual ISO-compliant inspection certificates and export organization audit logs.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start">
          <Button variant="outline" size="sm" onClick={handleExportCsv} className="gap-1.5">
            <FileDown className="h-3.5 w-3.5 text-brand-400" />
            Export Audit CSV
          </Button>
          <Button variant="outline" size="sm" onClick={fetchReports} isLoading={isLoading} className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh Archive
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-md bg-amber-950/60 border border-amber-800 text-amber-300 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Reports Table Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Certified Inspection Runs Archive</CardTitle>
          <CardDescription>
            Official digital records of vision inspection sessions, human review sign-offs, and PDF downloads.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Certificate ID</TableHead>
                <TableHead>Target Asset</TableHead>
                <TableHead>Created Date (UTC)</TableHead>
                <TableHead>AI Classification</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Review Decision</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-xs text-slate-500">
                    No inspection certificates found. Run visual inspections to generate compliance certificates.
                  </TableCell>
                </TableRow>
              ) : (
                reports.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-mono text-xs font-semibold text-slate-200">
                      #{r.id.slice(0, 8).toUpperCase()}
                    </TableCell>
                    <TableCell className="text-xs text-slate-300 font-mono">
                      {r.image?.original_filename || "N/A"}
                    </TableCell>
                    <TableCell className="text-xs text-slate-400">
                      {new Date(r.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-xs">
                      {r.result ? (
                        <span className="capitalize font-medium text-slate-200">
                          {r.result.predicted_class.replace(/_/g, " ")}
                        </span>
                      ) : (
                        <span className="text-slate-500">Pending</span>
                      )}
                    </TableCell>
                    <TableCell className="text-xs font-mono">
                      {r.result ? `${(r.result.confidence * 100).toFixed(1)}%` : "—"}
                    </TableCell>
                    <TableCell>
                      {r.review ? (
                        <Badge variant="success" className="font-mono text-[10px]">
                          {r.review.decision}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="font-mono text-[10px]">
                          AUTO
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link href={`/inspections/${r.id}`}>
                          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs gap-1">
                            <Eye className="h-3 w-3" />
                            View
                          </Button>
                        </Link>
                        <a href={getPdfUrl(r.id)} target="_blank" rel="noopener noreferrer">
                          <Button variant="outline" size="sm" className="h-7 px-2 text-xs gap-1 text-brand-400 border-brand-800">
                            <FileDown className="h-3 w-3" />
                            PDF
                          </Button>
                        </a>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
