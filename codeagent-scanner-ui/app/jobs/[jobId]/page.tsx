"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { JobProgress } from "@/components/jobs/job-progress";
import { JobLogs } from "@/components/jobs/job-logs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExportDropdown } from "@/components/ui/export-dropdown";
import { ArrowLeft, RefreshCw, X } from "lucide-react";
import Link from "next/link";
import { useJobStatus } from "@/lib/hooks/use-job-status";
import { useJobReport } from "@/lib/hooks/use-job-report";
import {
  cancelJob,
  rerunJob,
  getEnhancedReport,
  triggerEnhancedReport,
} from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { use, useState } from "react";
import {
  exportToHTML,
  exportToCSV,
  exportToMarkdown,
  exportToJSON,
  exportEnhancedToHTML,
  exportEnhancedToCSV,
  exportEnhancedToMarkdown,
  exportEnhancedToJSON,
  downloadFile,
  getExportConfig,
} from "@/lib/export-utils";

export default function JobDetailPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  // Unwrap params Promise for Next.js 16+
  const { jobId } = use(params);

  const { jobInfo, isLoading, error, isCompleted, isFailed, isRunning } =
    useJobStatus(jobId);
  const { data: report } = useJobReport(jobId, isCompleted);
  const { toast } = useToast();
  const router = useRouter();
  const [isActing, setIsActing] = useState(false);

  const handleCancelJob = async () => {
    // Check if job can still be cancelled
    if (jobInfo && !isRunning && jobInfo.status !== "queued") {
      toast({
        title: "⚠️ Cannot Cancel",
        description: `Job is already ${jobInfo.status}. Only running or queued jobs can be cancelled.`,
        variant: "destructive",
      });
      return;
    }

    if (!confirm("Are you sure you want to cancel this job?")) {
      console.log("[JobDetailPage] User cancelled the cancellation");
      return;
    }

    console.log("[JobDetailPage] Attempting to cancel job:", jobId);
    console.log("[JobDetailPage] Current job status:", jobInfo?.status);
    setIsActing(true);
    try {
      const result = await cancelJob(jobId);
      console.log("[JobDetailPage] Cancel job result:", result);
      toast({
        title: "✅ Job Cancelled",
        description: "The scan job has been cancelled",
      });

      // Force refresh the job status
      window.location.reload();
    } catch (err) {
      console.error("[JobDetailPage] Failed to cancel job:", err);
      toast({
        title: "❌ Failed to Cancel",
        description: (err as Error).message,
        variant: "destructive",
      });
    } finally {
      setIsActing(false);
    }
  };

  const handleRerunJob = async () => {
    console.log("[JobDetailPage] Attempting to rerun job:", jobId);
    setIsActing(true);
    try {
      const result = await rerunJob(jobId);
      console.log("[JobDetailPage] Rerun job result:", result);
      toast({
        title: "✅ Job Restarted",
        description: `New job ID: ${result.job_id}`,
      });
      router.push(`/jobs/${result.job_id}`);
    } catch (err) {
      console.error("[JobDetailPage] Failed to rerun job:", err);

      // Handle 404 specifically - feature not implemented
      const errorMessage = (err as Error).message;
      if (errorMessage.includes("404") || errorMessage.includes("not found")) {
        toast({
          title: "⚠️ Rerun Not Available",
          description:
            "Job rerun feature is not yet implemented in the backend. Please create a new scan instead.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "❌ Failed to Rerun",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      setIsActing(false);
    }
  };

  const handleExportReport = async (
    format: "html" | "csv" | "markdown" | "json",
    includeEnhanced: boolean
  ) => {
    if (!report) {
      toast({
        title: "❌ Report Not Available",
        description: "Wait for the scan to complete",
        variant: "destructive",
      });
      return;
    }

    try {
      let content: string;

      // Check if enhanced report is requested
      if (includeEnhanced) {
        try {
          // First, try to trigger AI analysis
          toast({
            title: "🤖 Preparing AI Analysis",
            description: "Checking for AI-enhanced report...",
          });

          // Trigger AI analysis (will return immediately if already exists)
          const triggerResult = await triggerEnhancedReport(jobId);

          if (triggerResult.status === "processing") {
            toast({
              title: "⏳ AI Analysis In Progress",
              description: `Analyzing ${triggerResult.issues_count} high/critical issues. This may take 1-2 minutes.`,
              duration: 5000,
            });

            // Wait a bit before trying to fetch
            await new Promise((resolve) => setTimeout(resolve, 2000));
          }

          // Fetch the enhanced report
          const enhancedReport = await getEnhancedReport(jobId);

          // Export with enhanced data
          switch (format) {
            case "html":
              content = exportEnhancedToHTML(enhancedReport);
              break;
            case "csv":
              content = exportEnhancedToCSV(enhancedReport);
              break;
            case "markdown":
              content = exportEnhancedToMarkdown(enhancedReport);
              break;
            case "json":
              content = exportEnhancedToJSON(enhancedReport);
              break;
            default:
              content = exportEnhancedToJSON(enhancedReport);
          }

          const config = getExportConfig(jobId, format);
          downloadFile(content, config.filename, config.mimeType);

          toast({
            title: "✅ Enhanced Report Exported",
            description:
              "AI-enhanced report with fixes downloaded successfully",
          });
          return;
        } catch (error) {
          // If enhanced report fails, show toast and fall back to regular report
          const errorMessage =
            error instanceof Error ? error.message : "Unknown error";

          if (
            errorMessage.includes("still be running") ||
            errorMessage.includes("not available yet")
          ) {
            toast({
              title: "⏳ AI Analysis In Progress",
              description:
                "Enhanced report not ready yet. Exporting regular report. Try again in 1-2 minutes for AI-enhanced version.",
              variant: "default",
              duration: 5000,
            });
          } else if (errorMessage.includes("OpenAI")) {
            toast({
              title: "⚠️ AI Analysis Not Available",
              description:
                "AI analysis is not configured. Exporting regular report.",
              variant: "default",
            });
          } else if (errorMessage.includes("No high or critical")) {
            toast({
              title: "ℹ️ No Critical Issues",
              description:
                "No high/critical issues found for AI analysis. Exporting regular report.",
              variant: "default",
            });
          } else {
            toast({
              title: "⚠️ Enhanced Report Not Available",
              description: "Exporting regular report instead.",
              variant: "default",
            });
          }
        }
      }

      // Export regular report
      switch (format) {
        case "html":
          content = exportToHTML(report);
          break;
        case "csv":
          content = exportToCSV(report);
          break;
        case "markdown":
          content = exportToMarkdown(report);
          break;
        case "json":
          content = exportToJSON(report);
          break;
        default:
          content = exportToJSON(report);
      }

      const config = getExportConfig(jobId, format);
      downloadFile(content, config.filename, config.mimeType);

      const formatNames = {
        html: "HTML Report",
        csv: "CSV Spreadsheet",
        markdown: "Markdown Document",
        json: "JSON Data",
      };

      toast({
        title: "✅ Report Exported",
        description: `${formatNames[format]} downloaded successfully`,
      });
    } catch (error) {
      toast({
        title: "❌ Export Failed",
        description: "Failed to export report. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Job Details" />
          <div className="p-6 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-muted">Loading job details...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !jobInfo) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Job Details" />
          <div className="p-6 flex items-center justify-center">
            <div className="text-center">
              <p className="text-error text-lg font-semibold mb-2">
                ❌ Failed to Load Job
              </p>
              <p className="text-muted mb-4">
                {error?.message || "Job not found"}
              </p>
              <Link href="/jobs">
                <Button>
                  <ArrowLeft size={18} />
                  Back to Jobs
                </Button>
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const statusVariant =
    jobInfo.status === "completed"
      ? "default"
      : jobInfo.status === "running" || jobInfo.status === "queued"
      ? "secondary"
      : jobInfo.status === "failed"
      ? "destructive"
      : "outline";

  const summary = report?.summary || {
    total_issues: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  };

  // Calculate total_issues for display
  const totalIssues =
    "total_issues" in summary
      ? summary.total_issues
      : summary.critical + summary.high + summary.medium + summary.low;

  // Calculate duration
  const duration =
    jobInfo.started_at && jobInfo.finished_at
      ? `${Math.round(
          (new Date(jobInfo.finished_at).getTime() -
            new Date(jobInfo.started_at).getTime()) /
            1000
        )}s`
      : jobInfo.started_at
      ? "In progress..."
      : "--";

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 md:ml-0">
        <Header title="Job Details" />
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/jobs">
                <Button variant="ghost" size="sm">
                  <ArrowLeft size={18} />
                </Button>
              </Link>
              <div>
                <p className="text-muted text-sm">Job ID: {jobId}</p>
                <h2 className="text-2xl font-bold">Code Scan</h2>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant={statusVariant}>{jobInfo.status}</Badge>

              {isRunning && (
                <Button
                  variant="outline"
                  className="border-border bg-transparent"
                  onClick={handleCancelJob}
                  disabled={isActing}
                >
                  <X size={18} />
                  {isActing ? "Cancelling..." : "Cancel"}
                </Button>
              )}

              {(isCompleted || isFailed) && (
                <>
                  <Button
                    variant="outline"
                    className="border-border bg-transparent"
                    onClick={() => {
                      toast({
                        title: "⚠️ Feature Not Available",
                        description:
                          "Job rerun is not yet implemented. Please create a new scan from the dashboard.",
                        variant: "destructive",
                      });
                    }}
                    disabled={isActing}
                  >
                    <RefreshCw size={18} />
                    Rerun (Coming Soon)
                  </Button>

                  <ExportDropdown
                    onExport={handleExportReport}
                    disabled={!report}
                    label="Export Report"
                  />
                </>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <JobProgress jobId={jobId} initialStatus={jobInfo} />
              <JobLogs jobId={jobId} />
            </div>
            <div className="bg-card border border-border rounded-lg p-6 h-fit">
              <h3 className="font-semibold mb-4">Scan Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted">Total Issues</span>
                  <span className="font-medium">{totalIssues}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Critical</span>
                  <span className="font-medium text-error">
                    {summary.critical}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">High</span>
                  <span className="font-medium text-warning">
                    {summary.high}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Medium</span>
                  <span className="font-medium">{summary.medium}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Low</span>
                  <span className="font-medium text-success">
                    {summary.low}
                  </span>
                </div>
                <div className="border-t border-border pt-3 mt-3">
                  <div className="flex justify-between">
                    <span className="text-muted">Duration</span>
                    <span className="font-medium">{duration}</span>
                  </div>
                  {jobInfo.progress !== undefined && (
                    <div className="flex justify-between mt-2">
                      <span className="text-muted">Progress</span>
                      <span className="font-medium">
                        {jobInfo.progress.percent}%
                      </span>
                    </div>
                  )}
                  {jobInfo.progress?.phase && (
                    <div className="flex justify-between mt-2">
                      <span className="text-muted">Current Phase</span>
                      <span className="font-medium text-sm">
                        {jobInfo.progress.phase}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
