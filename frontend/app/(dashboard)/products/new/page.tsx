"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Box, Cpu, Save, ArrowLeft, AlertCircle, Sliders } from "lucide-react";

const DEFECT_CLASSES_PRESET = [
  { id: "crazing", label: "Crazing (Micro-cracking)" },
  { id: "inclusion", label: "Inclusion (Foreign particle)" },
  { id: "patches", label: "Patches (Oxidation / Surface spots)" },
  { id: "pitted_surface", label: "Pitted Surface (Cavity defects)" },
  { id: "rolled-in_scale", label: "Rolled-in Scale (Mill scale)" },
  { id: "scratches", label: "Scratches (Abrasion / Gouges)" },
];

export default function NewProductPage() {
  const router = useRouter();

  const [name, setName] = React.useState("");
  const [sku, setSku] = React.useState("");
  const [code, setCode] = React.useState("");
  const [category, setCategory] = React.useState("Steel Surface");
  const [description, setDescription] = React.useState("");

  // AI Configuration state
  const [modelType, setModelType] = React.useState("BASELINE_CNN");
  const [confidenceThreshold, setConfidenceThreshold] = React.useState(0.80);
  const [selectedClasses, setSelectedClasses] = React.useState<string[]>([
    "crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"
  ]);

  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const toggleClass = (classId: string) => {
    if (selectedClasses.includes(classId)) {
      if (selectedClasses.length > 1) {
        setSelectedClasses(selectedClasses.filter((c) => c !== classId));
      }
    } else {
      setSelectedClasses([...selectedClasses, classId]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      await apiClient.post("/products", {
        name,
        sku,
        code,
        category,
        description: description || null,
        configuration: {
          model_type: modelType,
          confidence_threshold: confidenceThreshold,
          anomaly_threshold: 0.05,
          defect_classes: selectedClasses,
        },
      }, { headers });

      router.push("/products");
    } catch (err) {
      if (err instanceof ApiException) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Product creation failed. Verify inputs and permissions.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Box className="h-5 w-5 text-brand-400" />
            Register New Manufactured Product
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Define industrial part specifications and assign target deep learning inspection criteria.
          </p>
        </div>
        <Link href="/products">
          <Button variant="outline" size="sm" className="gap-1.5">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Catalog
          </Button>
        </Link>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-md bg-red-950/70 border border-red-800 text-xs text-red-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Card 1: Part Specifications */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">1. Part Specification & Inventory Identity</CardTitle>
            <CardDescription>
              Inventory tags and metadata matching facility ERP / MES systems.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Product Name"
                placeholder="e.g. Cold Rolled Steel Sheet #404"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <Input
                label="Manufacturing SKU"
                placeholder="e.g. CR-STEEL-404"
                value={sku}
                onChange={(e) => setSku(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Internal Product Code (Unique in Tenant)"
                placeholder="e.g. PRD-CR-404"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                helperText="Permanent identifier used by automated barcode/vision stations."
              />
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300">Category Sector</label>
                <select
                  className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="Steel Surface">Steel Surface</option>
                  <option value="Automobile Component">Automobile Component</option>
                  <option value="PCB & Electronics">PCB & Electronics</option>
                  <option value="Precision Castings">Precision Castings</option>
                  <option value="Extruded Aluminum">Extruded Aluminum</option>
                </select>
              </div>
            </div>

            <Input
              label="Technical Description / Quality Notes"
              placeholder="Dimensional tolerances, surface finish standard (e.g., ISO 8501-1)..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </CardContent>
        </Card>

        {/* Card 2: AI Model Inspection Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Cpu className="h-4 w-4 text-brand-400" />
              2. AI Quality Inspection Configuration
            </CardTitle>
            <CardDescription>
              Select the deep learning architecture and confidence gating for automated decisions.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300">Target Deep Learning Model</label>
                <select
                  className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono"
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                >
                  <option value="BASELINE_CNN">BASELINE_CNN (Custom 4-Block Convolutional Net)</option>
                  <option value="MOBILENET_V2">MOBILENET_V2 (Transfer Learning Pretrained Head)</option>
                  <option value="EFFICIENTNET_B0">EFFICIENTNET_B0 (High-Precision Feature Extraction)</option>
                  <option value="CONV_AUTOENCODER">CONV_AUTOENCODER (Unsupervised Anomaly Map)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-medium text-slate-300">Confidence Gate for Pass/Fail</label>
                  <span className="font-mono text-brand-400 font-bold">{Math.round(confidenceThreshold * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.50"
                  max="0.99"
                  step="0.01"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                  className="w-full accent-brand-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
                />
                <p className="text-[10px] text-slate-500">
                  Predictions with confidence below this threshold are routed to human Quality Managers.
                </p>
              </div>
            </div>

            {/* Defect Classes Selection */}
            <div className="space-y-2 pt-2 border-t border-slate-800/80">
              <label className="block text-xs font-medium text-slate-300">
                Monitored Surface Defect Categories (NEU Surface Defect Standards)
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {DEFECT_CLASSES_PRESET.map((c) => (
                  <label
                    key={c.id}
                    className={`flex items-center gap-2 p-2.5 rounded-md border text-xs cursor-pointer transition-colors ${
                      selectedClasses.includes(c.id)
                        ? "bg-brand-950/50 border-brand-700 text-slate-100"
                        : "bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedClasses.includes(c.id)}
                      onChange={() => toggleClass(c.id)}
                      className="accent-brand-500 h-3.5 w-3.5"
                    />
                    <span className="font-mono text-[11px]">{c.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end gap-2 border-t border-slate-800">
            <Link href="/products">
              <Button type="button" variant="outline" size="sm">
                Cancel
              </Button>
            </Link>
            <Button
              type="submit"
              variant="default"
              size="sm"
              isLoading={isLoading}
              className="gap-2"
            >
              <Save className="h-4 w-4" />
              Save & Register Product
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  );
}
