"use client";

import { Badge } from "@/components/ui/badge";
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { FileText } from "lucide-react";

interface Issue {
  id?: string;
  title?: string;
  severity?: string;
  file?: string;
  line?: number;
  tool?: string;
  description?: string;
}

interface IssuesTableProps {
  issues?: Issue[];
}

export function IssuesTable({ issues = [] }: IssuesTableProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (issues.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="p-6 border-b border-border">
          <h3 className="font-semibold">Detailed Issues</h3>
          <p className="text-sm text-muted mt-1">No issues found</p>
        </div>
        <EmptyState
          icon={FileText}
          title="No security issues detected"
          description="This scan found no vulnerabilities in the codebase."
        />
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="p-6 border-b border-border">
        <h3 className="font-semibold">Detailed Issues</h3>
        <p className="text-sm text-muted mt-1">
          {issues.length} {issues.length === 1 ? "issue" : "issues"} found
        </p>
      </div>
      <div className="divide-y divide-border">
        {issues.map((issue, index) => {
          const issueId = issue.id || `issue-${index}`;
          return (
            <div key={issueId}>
              <button
                onClick={() =>
                  setExpanded(expanded === issueId ? null : issueId)
                }
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-background/50 transition-colors text-left"
              >
                <div className="flex-1 flex items-center gap-4">
                  <ChevronDown
                    size={20}
                    className={`text-muted transition-transform ${
                      expanded === issueId ? "rotate-180" : ""
                    }`}
                  />
                  <div className="flex-1">
                    <p className="font-medium">
                      {issue.title || "Untitled Issue"}
                    </p>
                    <p className="text-sm text-muted mt-1">
                      {issue.file}:{issue.line || "N/A"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge
                    variant={
                      issue.severity === "critical"
                        ? "destructive"
                        : issue.severity === "high"
                        ? "secondary"
                        : "default"
                    }
                  >
                    {issue.severity || "medium"}
                  </Badge>
                  <span className="text-sm text-muted">
                    {issue.tool || "Unknown"}
                  </span>
                </div>
              </button>
              {expanded === issueId && (
                <div className="px-6 py-4 bg-background/50 border-t border-border">
                  <p className="text-sm mb-3">
                    {issue.description || "No description available"}
                  </p>
                  {issue.line && (
                    <div className="bg-background rounded p-3 font-mono text-xs text-muted">
                      <p>
                        Line {issue.line}: {issue.description || "N/A"}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
