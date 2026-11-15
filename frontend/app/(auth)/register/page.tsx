"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { AlertCircle, Building2, User, ArrowRight, CheckCircle2 } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [organizationName, setOrganizationName] = React.useState("");
  const [industry, setIndustry] = React.useState("Metal & Steel Manufacturing");
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (password.length < 8) {
      setErrorMessage("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.post<{
        tokens: { access_token: string; refresh_token: string };
        user: { id: string; email: string; full_name: string };
        active_organization_id: string;
      }>("/auth/register", {
        full_name: fullName,
        email,
        password,
        organization_name: organizationName,
        industry,
      });

      if (typeof window !== "undefined") {
        localStorage.setItem("ironory_access_token", response.tokens.access_token);
        localStorage.setItem("ironory_refresh_token", response.tokens.refresh_token);
        localStorage.setItem("ironory_org_id", response.active_organization_id);
      }

      router.push("/");
    } catch (err) {
      if (err instanceof ApiException) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Registration failed. Please check inputs and try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-slate-800 bg-slate-900/90 shadow-2xl">
      <CardHeader className="space-y-1">
        <CardTitle className="text-xl font-bold text-center">Register New Organization</CardTitle>
        <CardDescription className="text-center text-xs">
          Establish an isolated B2B SaaS tenant for visual defect inspection.
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {errorMessage && (
            <div className="flex items-start gap-2.5 p-3 rounded-md bg-red-950/60 border border-red-800/80 text-red-300 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Section: Facility Details */}
          <div className="space-y-3 pt-1 border-t border-slate-800/60">
            <div className="text-[11px] font-mono uppercase tracking-wider text-brand-400 flex items-center gap-1.5">
              <Building2 className="h-3.5 w-3.5" />
              Facility & Tenant Profile
            </div>
            <Input
              label="Company or Plant Name"
              placeholder="Apex Automotive Components Ltd."
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              required
            />
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-slate-300">Target Industry Sector</label>
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
          </div>

          {/* Section: Administrator Details */}
          <div className="space-y-3 pt-3 border-t border-slate-800/60">
            <div className="text-[11px] font-mono uppercase tracking-wider text-brand-400 flex items-center gap-1.5">
              <User className="h-3.5 w-3.5" />
              Primary Quality Administrator
            </div>
            <Input
              label="Full Name"
              placeholder="Dr. Evelyn Vance"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <Input
              label="Corporate Email Address"
              type="email"
              placeholder="e.vance@apex-components.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Master Password (min 8 chars, 1 uppercase, 1 digit)"
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              helperText="Must contain uppercase, lowercase, and numbers."
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-3">
          <Button
            type="submit"
            className="w-full gap-2"
            isLoading={isLoading}
          >
            Create Organization Tenant
            <ArrowRight className="h-4 w-4" />
          </Button>

          <div className="text-center text-xs text-slate-400">
            Already registered?{" "}
            <Link href="/login" className="text-brand-400 font-semibold hover:underline">
              Sign In
            </Link>
          </div>
        </CardFooter>
      </form>
    </Card>
  );
}
