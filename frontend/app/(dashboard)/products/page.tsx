"use client";

import * as React from "react";
import Link from "next/link";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { Box, Plus, Search, Cpu, CheckCircle2, AlertCircle, ScanEye } from "lucide-react";

interface Product {
  id: string;
  name: string;
  sku: string;
  code: string;
  description: string | null;
  category: string;
  is_active: boolean;
  created_at: string;
  configuration: {
    model_type: string;
    confidence_threshold: number;
    anomaly_threshold: number;
    defect_classes: string[];
  } | null;
}

export default function ProductsPage() {
  const [products, setProducts] = React.useState<Product[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [categoryFilter, setCategoryFilter] = React.useState("");
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const fetchProducts = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const params = new URLSearchParams();
      if (searchQuery) params.append("query", searchQuery);
      if (categoryFilter) params.append("category", categoryFilter);

      const url = `/products${params.toString() ? `?${params.toString()}` : ""}`;
      const data = await apiClient.get<Product[]>(url, { headers });
      setProducts(data);
    } catch (err) {
      if (err instanceof ApiException) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to load products. Verify active organization session.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchProducts();
  }, [categoryFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchProducts();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Box className="h-5 w-5 text-brand-400" />
              Product Catalog & Surface Inspection Profiles
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              Catalog Active
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Configure manufactured items, defect tolerances, and dedicated deep learning models.
          </p>
        </div>

        <Link href="/products/new">
          <Button variant="default" size="sm" className="gap-2">
            <Plus className="h-4 w-4" />
            Register Product
          </Button>
        </Link>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearch} className="flex gap-2 w-full sm:w-80">
          <Input
            placeholder="Search by name, SKU, or code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 text-xs"
          />
          <Button type="submit" variant="secondary" size="sm" className="h-8 px-2.5">
            <Search className="h-3.5 w-3.5" />
          </Button>
        </form>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 whitespace-nowrap">Filter Sector:</span>
          <select
            className="h-8 rounded-md border border-slate-700 bg-slate-900 px-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="Steel Surface">Steel Surface</option>
            <option value="Automobile Component">Automobile Component</option>
            <option value="PCB & Electronics">PCB & Electronics</option>
            <option value="Precision Castings">Precision Castings</option>
          </select>
        </div>
      </div>

      {/* Products Table Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Registered Inspection Items</CardTitle>
            <CardDescription>
              Parts actively routed for visual defect classification and anomaly scoring.
            </CardDescription>
          </div>
          <Badge variant="outline" className="font-mono text-[10px]">
            {products.length} Products Found
          </Badge>
        </CardHeader>
        <CardContent>
          {errorMessage && (
            <div className="p-3 mb-4 rounded-md bg-amber-950/60 border border-amber-800 text-amber-300 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-amber-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {products.length === 0 && !isLoading && (
            <EmptyState
              icon={<Box className="w-8 h-8 text-slate-500" />}
              title="No Products Configured"
              description="Register your first manufactured product or component to enable automated visual inspection."
              action={
                <Link href="/products/new">
                  <Button variant="default" size="sm" className="gap-2">
                    <Plus className="h-4 w-4" />
                    Register Product
                  </Button>
                </Link>
              }
            />
          )}

          {products.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Part Name & Code</TableHead>
                  <TableHead>SKU & Category</TableHead>
                  <TableHead>Assigned AI Architecture</TableHead>
                  <TableHead>Confidence Gate</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>
                      <div className="font-sans font-medium text-slate-100">{p.name}</div>
                      <div className="text-[11px] font-mono text-slate-500">{p.code}</div>
                    </TableCell>
                    <TableCell>
                      <div className="text-slate-300 font-mono text-xs">{p.sku}</div>
                      <div className="text-[11px] text-slate-500 font-sans">{p.category}</div>
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex items-center gap-1.5 font-mono text-xs text-brand-400">
                        <Cpu className="h-3.5 w-3.5" />
                        {p.configuration?.model_type || "BASELINE_CNN"}
                      </span>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-slate-300">
                      {Math.round((p.configuration?.confidence_threshold || 0.75) * 100)}%
                    </TableCell>
                    <TableCell>
                      <Badge variant={p.is_active ? "success" : "outline"} className="text-[10px]">
                        {p.is_active ? "Active" : "Archived"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Link href={`/inspections?product_id=${p.id}`}>
                        <Button variant="outline" size="sm" className="h-7 text-[11px] gap-1">
                          <ScanEye className="h-3 w-3" />
                          View Runs
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
