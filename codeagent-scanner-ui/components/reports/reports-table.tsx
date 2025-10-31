"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import { useReports } from "@/lib/hooks/use-reports";
import type { SeverityLevel } from "@/lib/api-client";

interface ReportsTableProps {
  severity?: SeverityLevel;
  tool?: string;
  repo?: string;
  since?: string;
  until?: string;
  label?: string;
}

export function ReportsTable({
  severity,
  tool,
  repo,
  since,
  until,
  label,
}: ReportsTableProps) {
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading, error } = useReports({
    page,
    limit,
    severity,
    tool,
    repo,
    since,
    until,
    label,
  });

  // Helper to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) return "Just now";
    if (diffHours < 24)
      return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    if (diffDays === 1) return "1 day ago";
    if (diffDays < 7) return `${diffDays} days ago`;

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-lg p-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted">Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-border rounded-lg p-12">
        <div className="text-center">
          <p className="text-error text-lg font-semibold mb-2">
            ❌ Failed to Load Reports
          </p>
          <p className="text-muted">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-12">
        <div className="text-center">
          <p className="text-muted text-lg mb-2">📋 No Reports Found</p>
          <p className="text-muted text-sm">
            Try adjusting your filters or submit a new scan
          </p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / limit);

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-background/50">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Job ID / Repository
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Critical
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                High
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Medium
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Low
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Tools Used
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Date
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-muted">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((report, index) => (
              <tr
                key={`${report.job_id}-${index}`}
                className="border-b border-border hover:bg-background/50 transition-colors"
              >
                <td className="px-6 py-4">
                  <div
                    className="font-medium truncate max-w-xs"
                    title={report.repo_url || report.job_id}
                  >
                    {report.repo_url || report.job_id}
                  </div>
                  {report.labels && report.labels.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {report.labels.slice(0, 3).map((label) => (
                        <span
                          key={label}
                          className="text-xs bg-background px-2 py-0.5 rounded"
                        >
                          {label}
                        </span>
                      ))}
                      {report.labels.length > 3 && (
                        <span className="text-xs text-muted">
                          +{report.labels.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4">
                  {report.summary.critical > 0 ? (
                    <span className="text-error font-medium">
                      {report.summary.critical}
                    </span>
                  ) : (
                    <span className="text-muted">0</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {report.summary.high > 0 ? (
                    <span className="text-warning font-medium">
                      {report.summary.high}
                    </span>
                  ) : (
                    <span className="text-muted">0</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {report.summary.medium > 0 ? (
                    <span className="font-medium">{report.summary.medium}</span>
                  ) : (
                    <span className="text-muted">0</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {report.summary.low > 0 ? (
                    <span className="text-success font-medium">
                      {report.summary.low}
                    </span>
                  ) : (
                    <span className="text-muted">0</span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-muted">
                  {report.tools.join(", ")}
                </td>
                <td className="px-6 py-4 text-sm text-muted">
                  {formatDate(report.generated_at)}
                </td>
                <td className="px-6 py-4 text-right">
                  <Link href={`/reports/${report.job_id}`}>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-primary hover:text-primary"
                    >
                      <ArrowRight size={16} />
                    </Button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="border-t border-border px-6 py-4 flex items-center justify-between">
          <p className="text-sm text-muted">
            Showing {(page - 1) * limit + 1} to{" "}
            {Math.min(page * limit, data.total)} of {data.total} reports
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="border-border"
            >
              <ChevronLeft size={16} />
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (page <= 3) {
                  pageNum = i + 1;
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = page - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={page === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => setPage(pageNum)}
                    className="w-8 h-8 p-0 border-border"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="border-border"
            >
              Next
              <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
