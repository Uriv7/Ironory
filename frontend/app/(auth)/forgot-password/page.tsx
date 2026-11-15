"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { AlertCircle, CheckCircle2, KeyRound, Mail, ArrowLeft, Lock } from "lucide-react";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [step, setStep] = React.useState<"request" | "reset">("request");
  const [email, setEmail] = React.useState("");
  const [resetToken, setResetToken] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [feedback, setFeedback] = React.useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    if (!email) {
      setFeedback({ type: "error", text: "Please enter your registered work email." });
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiClient.post<{ message: string; reset_token?: string }>("/auth/forgot-password", { email });
      setFeedback({
        type: "success",
        text: "Recovery instructions dispatched. If an account matches this email, a reset token has been issued.",
      });
      if (res.reset_token) {
        setResetToken(res.reset_token);
        setStep("reset");
      }
    } catch (err) {
      if (err instanceof ApiException) {
        setFeedback({ type: "error", text: err.message });
      } else {
        setFeedback({ type: "error", text: "Failed to request password reset. Try again later." });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    if (!resetToken || !newPassword) {
      setFeedback({ type: "error", text: "Please provide the reset token and your new password." });
      return;
    }

    if (newPassword.length < 8) {
      setFeedback({ type: "error", text: "New password must be at least 8 characters long." });
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post("/auth/reset-password", {
        token: resetToken,
        new_password: newPassword,
      });
      setFeedback({
        type: "success",
        text: "Password updated successfully! Redirecting to login...",
      });
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      if (err instanceof ApiException) {
        setFeedback({ type: "error", text: err.message });
      } else {
        setFeedback({ type: "error", text: "Password reset failed. Verify your token validity." });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-slate-800 bg-slate-900/90 shadow-2xl">
      <CardHeader className="space-y-1">
        <CardTitle className="text-xl font-bold text-center">
          {step === "request" ? "Recover Password" : "Set New Password"}
        </CardTitle>
        <CardDescription className="text-center text-xs">
          {step === "request"
            ? "Enter your account email to receive cryptographic password reset credentials."
            : "Enter your verification token and secure new password."}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {feedback && (
          <div
            className={`p-3 mb-4 rounded-md text-xs flex items-center gap-2 ${
              feedback.type === "success"
                ? "bg-emerald-950/70 border border-emerald-800 text-emerald-300"
                : "bg-red-950/70 border border-red-800 text-red-300"
            }`}
          >
            {feedback.type === "success" ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="h-4 w-4 text-red-400 shrink-0" />
            )}
            <span>{feedback.text}</span>
          </div>
        )}

        {step === "request" ? (
          <form onSubmit={handleRequestReset} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Registered Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <Input
                  type="email"
                  placeholder="inspector@metallurgy.com"
                  className="pl-9 bg-slate-950 border-slate-700"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <Button type="submit" variant="default" className="w-full gap-2" isLoading={isLoading}>
              <KeyRound className="h-4 w-4" />
              Send Reset Credentials
            </Button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Reset Token</label>
              <Input
                type="text"
                placeholder="Paste signed token..."
                className="bg-slate-950 border-slate-700 font-mono text-xs"
                value={resetToken}
                onChange={(e) => setResetToken(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">New Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <Input
                  type="password"
                  placeholder="Min. 8 characters"
                  className="pl-9 bg-slate-950 border-slate-700"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <Button type="submit" variant="default" className="w-full gap-2" isLoading={isLoading}>
              <CheckCircle2 className="h-4 w-4" />
              Update Password
            </Button>
          </form>
        )}
      </CardContent>

      <CardFooter className="flex justify-between border-t border-slate-800/80 pt-4">
        <Link
          href="/login"
          className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="h-3 w-3" />
          Back to Sign In
        </Link>
        {step === "reset" && (
          <button
            type="button"
            onClick={() => setStep("request")}
            className="text-xs text-slate-400 hover:text-slate-200"
          >
            Re-enter Email
          </button>
        )}
      </CardFooter>
    </Card>
  );
}
