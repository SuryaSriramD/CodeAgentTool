"use client";

import { useEffect, useState } from "react";
import { streamJobEvents } from "@/lib/api-client";

interface JobLogsProps {
  jobId: string;
}

export function JobLogs({ jobId }: JobLogsProps) {
  const [logs, setLogs] = useState<string[]>([
    "[INFO] Starting vulnerability scan...",
  ]);
  const [lastStatus, setLastStatus] = useState<string | null>(null);

  useEffect(() => {
    let eventSource: EventSource | null = null;

    try {
      eventSource = streamJobEvents(
        jobId,
        (event) => {
          console.log("[v0] Job event received:", event);

          // Track job status
          if (event.status) {
            setLastStatus(event.status);
          }

          // Add log messages based on progress phase
          if (event.progress?.phase) {
            const phaseMessages: Record<string, string> = {
              init: "Initializing scan...",
              clone: "Cloning repository...",
              analyze: "Running security analyzers...",
              aggregate: "Aggregating results...",
              write: "Generating report...",
            };
            const message =
              phaseMessages[event.progress.phase] || event.progress.phase;
            setLogs((prevLogs) => {
              const lastLog = prevLogs[prevLogs.length - 1];
              // Avoid duplicate messages
              if (!lastLog.includes(message)) {
                return [...prevLogs, `[INFO] ${message}`];
              }
              return prevLogs;
            });
          }

          // Add completion message
          if (event.status === "completed") {
            setLogs((prevLogs) => [
              ...prevLogs,
              "[INFO] Scan completed successfully",
            ]);
          } else if (event.status === "failed") {
            setLogs((prevLogs) => [
              ...prevLogs,
              `[ERROR] Scan failed: ${event.error || "Unknown error"}`,
            ]);
          }
        },
        (error) => {
          console.error("[v0] SSE error:", error);
          // Only show connection error if job wasn't in a terminal state
          const terminalStates = ["completed", "failed", "canceled"];
          if (!lastStatus || !terminalStates.includes(lastStatus)) {
            setLogs((prevLogs) => [...prevLogs, "[ERROR] Connection lost"]);
          }
        }
      );
    } catch (error) {
      console.error("[v0] Failed to connect to job stream:", error);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [jobId]);

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="font-semibold mb-4">Scan Logs</h3>
      <div className="bg-background rounded p-4 font-mono text-sm space-y-1 max-h-64 overflow-y-auto">
        {logs.map((log, index) => (
          <div
            key={index}
            className="text-muted hover:text-foreground transition-colors"
          >
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
