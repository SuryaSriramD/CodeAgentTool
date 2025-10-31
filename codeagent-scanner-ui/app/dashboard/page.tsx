"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { KPICard } from "@/components/dashboard/kpi-card";
import { RecentJobs } from "@/components/dashboard/recent-jobs";
import { SeverityDistributionChart } from "@/components/dashboard/severity-distribution-chart";
import { NewScanButton } from "@/components/dashboard/new-scan-button";
import {
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useDashboardStats } from "@/lib/hooks/use-dashboard-stats";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function Dashboard() {
  const { data: stats, isLoading, error } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Dashboard" />
          <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p className="text-muted">Loading dashboard...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Dashboard" />
          <div className="p-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {error.message ||
                  "Failed to load dashboard data. Please try again."}
              </AlertDescription>
            </Alert>
          </div>
        </main>
      </div>
    );
  }

  const totalIssues =
    (stats?.severity_distribution.critical || 0) +
    (stats?.severity_distribution.high || 0) +
    (stats?.severity_distribution.medium || 0) +
    (stats?.severity_distribution.low || 0);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 md:ml-0">
        <Header title="Dashboard" />
        <div className="p-6 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-muted text-sm">Welcome back</p>
              <h2 className="text-3xl font-bold mt-1">
                Vulnerability Overview
              </h2>
            </div>
            <NewScanButton />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              title="Total Scans"
              value={stats?.total_scans.toLocaleString() || "0"}
              icon={BarChart3}
              trend={`${stats?.ai_enhanced_reports || 0} AI-enhanced`}
            />
            <KPICard
              title="Active Jobs"
              value={stats?.active_jobs.toString() || "0"}
              icon={Clock}
              trend={stats?.active_jobs ? "In progress" : "All complete"}
              variant={stats?.active_jobs ? "default" : "success"}
            />
            <KPICard
              title="Critical Issues"
              value={stats?.severity_distribution.critical.toString() || "0"}
              icon={AlertCircle}
              trend={`${totalIssues} total issues`}
              variant="error"
            />
            <KPICard
              title="Total Issues"
              value={totalIssues.toLocaleString()}
              icon={CheckCircle}
              trend={`${stats?.severity_distribution.high || 0} high severity`}
              variant="default"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <RecentJobs recentScans={stats?.recent_scans} />
            </div>
            <div>
              <SeverityDistributionChart data={stats?.severity_distribution} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
