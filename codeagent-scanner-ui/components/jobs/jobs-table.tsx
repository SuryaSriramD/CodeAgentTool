"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { FileText } from "lucide-react";
import { useReports } from "@/lib/hooks/use-reports";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorDisplay } from "@/components/ui/error-display";
import { formatDistanceToNow } from "date-fns";

interface JobsTableProps {
  statusFilter: string;
  searchQuery: string;
}

export function JobsTable({ statusFilter, searchQuery }: JobsTableProps) {
  const {
    data: reportsData,
    isLoading,
    error,
    refetch,
  } = useReports({ page: 1, limit: 100 });

  const filteredJobs = useMemo(() => {
    if (!reportsData?.items) return [];

    let filtered = reportsData.items.map((report: any) => ({
      id: report.job_id,
      repo: report.repo_url || "Unknown Repository",
      status: "completed", // Reports are always completed
      issues:
        (report.summary?.critical || 0) +
        (report.summary?.high || 0) +
        (report.summary?.medium || 0) +
        (report.summary?.low || 0),
      critical: report.summary?.critical || 0,
      duration: "-", // Duration not available in reports API
      timestamp: report.generated_at,
      tools: report.tools || [],
    }));

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter((job: any) =>
        job.repo.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [reportsData, searchQuery, statusFilter]);

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "running":
      case "queued":
        return "secondary";
      case "failed":
      case "canceled":
        return "destructive";
      default:
        return "default";
    }
  };

  const formatStatus = (status: string) => {
    if (status === "running") return "In Progress";
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-lg p-12">
        <LoadingSpinner size="lg" className="mx-auto" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-border rounded-lg">
        <ErrorDisplay
          title="Failed to load jobs"
          message="Unable to fetch scan jobs from the server."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  if (filteredJobs.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg">
        <EmptyState
          icon={FileText}
          title="No jobs found"
          description={
            searchQuery
              ? `No jobs match "${searchQuery}"`
              : statusFilter !== "all"
              ? `No jobs with status "${formatStatus(statusFilter)}"`
              : "No scan jobs available. Submit a scan to get started."
          }
        />
      </div>
    );
  }

  const totalJobs = reportsData?.total || filteredJobs.length;

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-background/50">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Repository
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Issues
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Critical
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Tools
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Time
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-muted">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredJobs.map((job: any, index: number) => (
              <tr
                key={`${job.id}-${index}`}
                className="border-b border-border hover:bg-background/50 transition-colors"
              >
                <td className="px-6 py-4 font-medium">{job.repo}</td>
                <td className="px-6 py-4">
                  <Badge variant={getStatusBadgeVariant(job.status)}>
                    {formatStatus(job.status)}
                  </Badge>
                </td>
                <td className="px-6 py-4">{job.issues}</td>
                <td className="px-6 py-4">
                  {job.critical > 0 ? (
                    <span className="text-error font-medium">
                      {job.critical}
                    </span>
                  ) : (
                    <span className="text-success">0</span>
                  )}
                </td>
                <td className="px-6 py-4 text-muted text-sm">
                  {job.tools.length > 0 ? job.tools.join(", ") : "-"}
                </td>
                <td className="px-6 py-4 text-muted text-sm">
                  {formatTimestamp(job.timestamp)}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    <Link href={`/jobs/${job.id}`}>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-primary hover:text-primary"
                      >
                        <ArrowRight size={16} />
                      </Button>
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-3 border-t border-border bg-background/50">
        <p className="text-sm text-muted">
          Showing {filteredJobs.length} of {totalJobs} jobs
        </p>
      </div>
    </div>
  );
}
