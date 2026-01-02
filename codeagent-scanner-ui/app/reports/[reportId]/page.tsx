"use client";

import { use } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { SeverityChart } from "@/components/reports/severity-chart";
import { IssuesTable } from "@/components/reports/issues-table";
import { Button } from "@/components/ui/button";
import { ExportDropdown } from "@/components/ui/export-dropdown";
import { ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useReportDetail } from "@/lib/hooks/use-report-detail";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
import { getEnhancedReport, triggerEnhancedReport } from "@/lib/api-client";

export default function ReportDetailPage({
  params,
}: {
  params: Promise<{ reportId: string }>;
}) {
  // Unwrap params Promise for Next.js 16+
  const { reportId } = use(params);
  const { data: report, isLoading, error } = useReportDetail(reportId);
  const { toast } = useToast();

  const handleDownloadReport = async (
    format: "html" | "csv" | "markdown" | "json",
    includeEnhanced: boolean
  ) => {
    if (!report) return;

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
          const triggerResult = await triggerEnhancedReport(reportId);

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
          const enhancedReport = await getEnhancedReport(reportId);

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

          const config = getExportConfig(reportId, format);
          downloadFile(content, config.filename, config.mimeType);

          toast({
            title: "✅ Enhanced Report Downloaded",
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
                "Enhanced report not ready yet. Downloading regular report. Try again in 1-2 minutes for AI-enhanced version.",
              variant: "default",
              duration: 5000,
            });
          } else if (errorMessage.includes("OpenAI")) {
            toast({
              title: "⚠️ AI Analysis Not Available",
              description:
                "AI analysis is not configured. Downloading regular report.",
              variant: "default",
            });
          } else if (errorMessage.includes("No high or critical")) {
            toast({
              title: "ℹ️ No Critical Issues",
              description:
                "No high/critical issues found for AI analysis. Downloading regular report.",
              variant: "default",
            });
          } else {
            toast({
              title: "⚠️ Enhanced Report Not Available",
              description: "Downloading regular report instead.",
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

      const config = getExportConfig(reportId, format);
      downloadFile(content, config.filename, config.mimeType);

      const formatNames = {
        html: "HTML Report",
        csv: "CSV Spreadsheet",
        markdown: "Markdown Document",
        json: "JSON Data",
      };

      toast({
        title: "✅ Report Downloaded",
        description: `${formatNames[format]} downloaded successfully`,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to download the report. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Report Details" />
          <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p className="text-muted">Loading report...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0">
          <Header title="Report Details" />
          <div className="p-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {error?.message || "Failed to load report. Please try again."}
              </AlertDescription>
            </Alert>
            <Link href="/reports">
              <Button variant="outline" className="mt-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Reports
              </Button>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const totalIssues =
    (report.summary?.critical || 0) +
    (report.summary?.high || 0) +
    (report.summary?.medium || 0) +
    (report.summary?.low || 0);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 md:ml-0">
        <Header title="Report Details" />
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/reports">
                <Button variant="ghost" size="sm">
                  <ArrowLeft size={18} />
                </Button>
              </Link>
              <div>
                <p className="text-muted text-sm">Report ID: {reportId}</p>
                <h2 className="text-2xl font-bold">
                  {report.meta?.repo?.url || "Repository"}
                </h2>
              </div>
            </div>

            <ExportDropdown
              onExport={handleDownloadReport}
              label="Download Report"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-muted text-sm">Critical Issues</p>
              <p className="text-3xl font-bold text-error mt-2">
                {report.summary?.critical || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-muted text-sm">High Issues</p>
              <p className="text-3xl font-bold text-warning mt-2">
                {report.summary?.high || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-muted text-sm">Medium Issues</p>
              <p className="text-3xl font-bold mt-2">
                {report.summary?.medium || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-4">
              <p className="text-muted text-sm">Total Issues</p>
              <p className="text-3xl font-bold mt-2">{totalIssues}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <SeverityChart
                data={{
                  critical: report.summary?.critical || 0,
                  high: report.summary?.high || 0,
                  medium: report.summary?.medium || 0,
                  low: report.summary?.low || 0,
                }}
              />
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Affected Files</h3>
              <div className="space-y-2">
                {report.files && report.files.length > 0 ? (
                  report.files.slice(0, 8).map((fileIssue, index) => (
                    <div
                      key={index}
                      className="p-3 bg-background rounded hover:bg-background/80 transition-colors cursor-pointer"
                    >
                      <p className="text-sm font-medium break-all">
                        {fileIssue.path}
                      </p>
                      <p className="text-xs text-muted mt-1">
                        {fileIssue.issues.length}{" "}
                        {fileIssue.issues.length === 1 ? "issue" : "issues"}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted">No files affected</p>
                )}
                {report.files && report.files.length > 8 && (
                  <p className="text-xs text-muted text-center pt-2">
                    + {report.files.length - 8} more files
                  </p>
                )}
              </div>
            </div>
          </div>

          <IssuesTable issues={report.files?.flatMap((f) => f.issues) || []} />
        </div>
      </main>
    </div>
  );
}
