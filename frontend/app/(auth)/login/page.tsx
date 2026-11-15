"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { AlertCircle, Lock, Mail, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email || !password) {
      setErrorMessage("Please enter both work email and password.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.post<{
        tokens: { access_token: string; refresh_token: string };
        user: { id: string; email: string; full_name: string };
        active_organization_id: string;
      }>("/auth/login", { email, password });

      // Store tokens for client sessions
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
        setErrorMessage("Authentication failed. Please verify credentials or backend availability.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-slate-800 bg-slate-900/90 shadow-2xl">
      <CardHeader className="space-y-1">
        <CardTitle className="text-xl font-bold text-center">Sign In to Inspection Hub</CardTitle>
        <CardDescription className="text-center text-xs">
          Access your manufacturing facility inspection records and models.
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

          <div className="space-y-1.5">
            <Input
              label="Work Email Address"
              type="email"
              placeholder="operator@manufacturing-corp.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">Password</label>
              <Link href="/forgot-password" className="text-[11px] text-brand-400 hover:text-brand-300">
                Forgot password?
              </Link>
            </div>
            <Input
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-3">
          <Button
            type="submit"
            className="w-full gap-2"
            isLoading={isLoading}
          >
            Authenticate & Launch Dashboard
            <ArrowRight className="h-4 w-4" />
          </Button>

          <div className="text-center text-xs text-slate-400">
            Need an enterprise account?{" "}
            <Link href="/register" className="text-brand-400 font-semibold hover:underline">
              Register Organization
            </Link>
          </div>
        </CardFooter>
      </form>
    </Card>
  );
}
