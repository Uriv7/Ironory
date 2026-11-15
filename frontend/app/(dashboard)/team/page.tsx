"use client";

import * as React from "react";
import { apiClient, ApiException } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { Users, UserPlus, Shield, Mail, CheckCircle2, AlertCircle, X, ShieldAlert } from "lucide-react";

interface Member {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: "OWNER" | "ADMIN" | "QUALITY_MANAGER" | "INSPECTOR" | "READ_ONLY";
  is_active: boolean;
  created_at: string;
}

export default function TeamManagementPage() {
  const [members, setMembers] = React.useState<Member[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  // Invite modal state
  const [isInviteOpen, setIsInviteOpen] = React.useState(false);
  const [inviteEmail, setInviteEmail] = React.useState("");
  const [inviteRole, setInviteRole] = React.useState<Member["role"]>("INSPECTOR");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [inviteFeedback, setInviteFeedback] = React.useState<string | null>(null);

  const fetchMembers = async () => {
    setIsLoading(true);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      const data = await apiClient.get<Member[]>("/organizations/members", { headers });
      setMembers(data);
    } catch (err) {
      if (err instanceof ApiException) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Unable to fetch organization team members. Ensure you are signed in.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchMembers();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setInviteFeedback(null);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("ironory_access_token") : null;
      const orgId = typeof window !== "undefined" ? localStorage.getItem("ironory_org_id") : null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (orgId) headers["X-Organization-ID"] = orgId;

      await apiClient.post("/organizations/invitations", {
        email: inviteEmail,
        role: inviteRole,
      }, { headers });

      setInviteFeedback(`Successfully invited ${inviteEmail} as ${inviteRole}`);
      setInviteEmail("");
      setIsInviteOpen(false);
      fetchMembers();
    } catch (err) {
      if (err instanceof ApiException) {
        setInviteFeedback(`Error: ${err.message}`);
      } else {
        setInviteFeedback("Invitation failed. Please verify user permissions.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRoleBadgeVariant = (role: Member["role"]) => {
    switch (role) {
      case "OWNER":
        return "default";
      case "ADMIN":
        return "warning";
      case "QUALITY_MANAGER":
        return "success";
      case "INSPECTOR":
        return "outline";
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Users className="h-5 w-5 text-brand-400" />
              Team Members & Role-Based Access
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              Multi-Tenant RBAC
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage organization inspectors, quality managers, and tenant role assignments.
          </p>
        </div>

        <Button
          onClick={() => setIsInviteOpen(true)}
          variant="default"
          size="sm"
          className="gap-2"
        >
          <UserPlus className="h-4 w-4" />
          Invite Team Member
        </Button>
      </div>

      {inviteFeedback && (
        <div className="p-3 rounded-md bg-slate-900 border border-brand-800 text-xs text-brand-300 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-brand-400" />
          <span>{inviteFeedback}</span>
        </div>
      )}

      {/* Invite Modal Dialog */}
      {isInviteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <Card className="w-full max-w-md border-slate-700 bg-slate-900 shadow-2xl">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm">Invite New Member</CardTitle>
                <CardDescription>Grant inspection and review privileges within this tenant.</CardDescription>
              </div>
              <button
                onClick={() => setIsInviteOpen(false)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </CardHeader>
            <form onSubmit={handleInvite}>
              <CardContent className="space-y-4">
                <Input
                  label="Colleague Email Address"
                  type="email"
                  placeholder="inspector@company.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  required
                />
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300">Assigned Organization Role</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-slate-700 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as Member["role"])}
                  >
                    <option value="INSPECTOR">Quality Inspector (Upload & Inspect)</option>
                    <option value="QUALITY_MANAGER">Quality Manager (Review & Approve)</option>
                    <option value="ADMIN">Organization Admin (Manage Products & Team)</option>
                    <option value="READ_ONLY">Read Only (View Dashboards & Reports)</option>
                  </select>
                </div>
              </CardContent>
              <div className="flex items-center justify-end gap-2 p-4 border-t border-slate-800">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsInviteOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="default" size="sm" isLoading={isSubmitting}>
                  Send Invitation
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Members Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Active Organization Roster</CardTitle>
            <CardDescription>
              Authorized personnel with access to this tenant&apos;s quality operations.
            </CardDescription>
          </div>
          <Badge variant="outline" className="font-mono text-[10px]">
            {members.length} Members Registered
          </Badge>
        </CardHeader>
        <CardContent>
          {errorMessage && (
            <div className="p-3 mb-4 rounded-md bg-amber-950/60 border border-amber-800 text-amber-300 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-amber-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {members.length === 0 && !isLoading && (
            <EmptyState
              icon={<Users className="w-8 h-8 text-slate-500" />}
              title="No Team Members Loaded"
              description="Sign in or register an account to view and invite team members."
              action={
                <Button variant="default" size="sm" onClick={() => setIsInviteOpen(true)}>
                  Invite First Colleague
                </Button>
              }
            />
          )}

          {members.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Member Name</TableHead>
                  <TableHead>Email Address</TableHead>
                  <TableHead>Assigned Role</TableHead>
                  <TableHead>Account Status</TableHead>
                  <TableHead>Joined Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell className="font-sans font-medium text-slate-100">
                      {member.full_name}
                    </TableCell>
                    <TableCell className="text-slate-400">{member.email}</TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(member.role)} className="font-mono text-[10px]">
                        {member.role.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                        Active
                      </span>
                    </TableCell>
                    <TableCell className="text-slate-500">
                      {new Date(member.created_at).toLocaleDateString()}
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
