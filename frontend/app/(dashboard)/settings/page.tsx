"use client";

import * as React from "react";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Settings, Building2, Save, CheckCircle2, AlertCircle } from "lucide-react";

interface OrganizationProfile {
  id: string;
  name: string;
  slug: string;
  industry: string | null;
  contact_email: string | null;
  logo_url: string | null;
  is_active: boolean;
  created_at: string;
}

export default function OrganizationSettingsPage() {
  const [profile, setProfile] = React.useState<OrganizationProfile | null>(null);
  const [name, setName] = React.useState("");
  const [industry, setIndustry] = React.useState("");
  const [contactEmail, setContactEmail] = React.useState("");
  const [logoUrl, setLogoUrl] = React.useState("");

  const [isLoading, setIsLoading] = React.useState(true);
  const [isSaving, setIsSaving] = React.useState(false);
  const [statusMessage, setStatusMessage] = React.useState<{ type: "success" | "error"; text: string } | null>(null);

  React.useEffect(() => {
    const fetchOrg = async () => {
      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
        const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;
        if (orgId) headers["X-Organization-ID"] = orgId;

        const data = await apiClient.get<OrganizationProfile>("/organizations/current", { headers });
        setProfile(data);
        setName(data.name);
        setIndustry(data.industry || "");
        setContactEmail(data.contact_email || "");
        setLogoUrl(data.logo_url || "");
      } catch (err) {
        if (err instanceof ApiException) {
          setStatusMessage({ type: "error", text: err.message });
        } else {
          setStatusMessage({ type: "error", text: "Failed to load organization settings. Verify active session." });
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrg();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMessage(null);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const updated = await apiClient.patch<OrganizationProfile>("/organizations/current", {
        name,
        industry: industry || null,
        contact_email: contactEmail || null,
        logo_url: logoUrl || null,
      }, { headers });

      setProfile(updated);
      setStatusMessage({ type: "success", text: "Organization profile updated successfully." });
    } catch (err) {
      if (err instanceof ApiException) {
        setStatusMessage({ type: "error", text: err.message });
      } else {
        setStatusMessage({ type: "error", text: "Save failed. Ensure your role is Owner or Admin." });
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Settings className="h-5 w-5 text-brand-400" />
            Tenant Profile & Operational Settings
          </h2>
          <Badge variant="outline" className="font-mono text-[10px]">
            Tenant Config
          </Badge>
        </div>
        <p className="text-xs text-slate-400 mt-0.5">
          Configure facility metadata, industry compliance parameters, and reporting defaults.
        </p>
      </div>

      {statusMessage && (
        <div
          className={`p-3 rounded-md text-xs flex items-center gap-2 ${
            statusMessage.type === "success"
              ? "bg-emerald-950/70 border border-emerald-800 text-emerald-300"
              : "bg-red-950/70 border border-red-800 text-red-300"
          }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-400" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Manufacturing Facility Profile</CardTitle>
            <CardDescription>
              Organization-level details printed on quality inspection compliance reports.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Company or Plant Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Apex Precision Alloys"
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="System Tenant Slug (Permanent URL Identifier)"
                value={profile?.slug || "org-slug"}
                disabled
                helperText="Tenant slugs are assigned upon organization creation."
              />
              <Input
                label="Primary Contact Email"
                type="email"
                value={contactEmail}
                onChange={(e) => setContactEmail(e.target.value)}
                placeholder="quality-compliance@company.com"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300">Industry Sector</label>
              <select
                className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
              >
                <option value="Metal & Steel Manufacturing">Metal & Steel Manufacturing</option>
                <option value="Automobile Component Manufacturing">Automobile Component Manufacturing</option>
                <option value="Electronics & PCB Manufacturing">Electronics & PCB Manufacturing</option>
                <option value="Plastic Injection Molding">Plastic Injection Molding</option>
                <option value="General Industrial Manufacturing">General Industrial Manufacturing</option>
              </select>
            </div>

            <Input
              label="Company Logo Asset URL"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              placeholder="https://assets.company.com/branding/logo.png"
              helperText="Rendered on generated quality audit PDF certificates."
            />
          </CardContent>
          <CardFooter className="flex justify-end gap-2 border-t border-slate-800">
            <Button
              type="submit"
              variant="default"
              size="sm"
              isLoading={isSaving}
              className="gap-2"
            >
              <Save className="h-4 w-4" />
              Save Settings
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  );
}
