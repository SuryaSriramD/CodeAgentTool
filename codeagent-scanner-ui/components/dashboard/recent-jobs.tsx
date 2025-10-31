"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { EmptyState } from "@/components/ui/empty-state";
import { FileText } from "lucide-react";

interface RecentScan {
  job_id: string;
  generated_at: string;
  total_issues: number;
  has_ai_analysis: boolean;
}

interface RecentJobsProps {
  recentScans?: RecentScan[];
}

export function RecentJobs({ recentScans = [] }: RecentJobsProps) {
  if (recentScans.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="p-6 border-b border-border">
          <h3 className="text-lg font-semibold">Recent Scan Jobs</h3>
          <p className="text-sm text-muted mt-1">No scans completed yet</p>
        </div>
        <EmptyState
          icon={FileText}
          title="No recent scans"
          description="Submit a scan to see results here."
        />
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="p-6 border-b border-border">
        <h3 className="text-lg font-semibold">Recent Scan Jobs</h3>
        <p className="text-sm text-muted mt-1">
          {recentScans.length} {recentScans.length === 1 ? "scan" : "scans"}{" "}
          completed
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Job ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Issues Found
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                AI Analysis
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted">
                Generated
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-muted">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {recentScans.map((scan) => (
              <tr
                key={scan.job_id}
                className="border-b border-border hover:bg-background/50 transition-colors"
              >
                <td className="px-6 py-4 font-medium font-mono text-sm">
                  {scan.job_id.substring(0, 8)}...
                </td>
                <td className="px-6 py-4">
                  <Badge
                    variant={scan.total_issues > 10 ? "destructive" : "default"}
                  >
                    {scan.total_issues}{" "}
                    {scan.total_issues === 1 ? "issue" : "issues"}
                  </Badge>
                </td>
                <td className="px-6 py-4">
                  {scan.has_ai_analysis ? (
                    <div className="flex items-center gap-2 text-primary">
                      <Sparkles size={16} />
                      <span className="text-sm">Available</span>
                    </div>
                  ) : (
                    <span className="text-sm text-muted">Not available</span>
                  )}
                </td>
                <td className="px-6 py-4 text-muted text-sm">
                  {formatDistanceToNow(new Date(scan.generated_at), {
                    addSuffix: true,
                  })}
                </td>
                <td className="px-6 py-4 text-right">
                  <Link href={`/reports/${scan.job_id}`}>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-primary hover:text-primary"
                    >
                      View Report
                      <ArrowRight size={16} className="ml-2" />
                    </Button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-4 border-t border-border">
        <Link href="/reports">
          <Button variant="outline" className="w-full bg-transparent">
            View All Reports
          </Button>
        </Link>
      </div>
    </div>
  );
}
