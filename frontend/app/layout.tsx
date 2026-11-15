import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "Ironory — Industrial Quality Inspection Platform",
  description: "Detect Defects. Ensure Quality. Build Trust. AI-powered industrial surface quality inspection.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
