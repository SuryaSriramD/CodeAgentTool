"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Clock, Loader, AlertCircle } from "lucide-react";
import { streamJobEvents, type JobInfo } from "@/lib/api-client";

interface Step {
  name: string;
  status: "pending" | "in-progress" | "completed" | "failed";
  time?: string;
}

interface JobProgressProps {
  jobId: string;
  initialStatus?: JobInfo;
}

export function JobProgress({ jobId, initialStatus }: JobProgressProps) {
  const [steps, setSteps] = useState<Step[]>([
    { name: "Initializing", status: "pending" },
    { name: "Cloning Repository", status: "pending" },
    { name: "Analyzing Code", status: "pending" },
    { name: "Generating Report", status: "pending" },
  ]);
  const [currentProgress, setCurrentProgress] = useState(0);

  useEffect(() => {
    // Set initial status if provided
    if (initialStatus) {
      updateStepsFromStatus(initialStatus);
    }

    let eventSource: EventSource | null = null;
    let lastStatus: string | null = initialStatus?.status || null;

    try {
      eventSource = streamJobEvents(
        jobId,
        (jobInfo) => {
          console.log("[JobProgress] Received job update:", jobInfo);
          lastStatus = jobInfo.status;
          updateStepsFromStatus(jobInfo);
        },
        (error) => {
          console.error("[JobProgress] SSE error:", error);
          // Only log error if job wasn't in a terminal state
          const terminalStates = ["completed", "failed", "canceled"];
          if (!lastStatus || !terminalStates.includes(lastStatus)) {
            console.error("[JobProgress] Unexpected SSE disconnection");
          }
        }
      );
    } catch (error) {
      console.error("[JobProgress] Failed to connect to job stream:", error);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [jobId, initialStatus]);

  const updateStepsFromStatus = (jobInfo: JobInfo) => {
    const { status, progress } = jobInfo;
    const progressPercent = progress?.percent || 0;
    setCurrentProgress(progressPercent);

    setSteps((prevSteps) => {
      const newSteps = [...prevSteps];

      // Map progress to steps
      if (status === "queued") {
        newSteps[0] = { ...newSteps[0], status: "in-progress" };
      } else if (status === "running") {
        newSteps[0] = { ...newSteps[0], status: "completed" };

        if (progressPercent <= 25) {
          newSteps[1] = { ...newSteps[1], status: "in-progress" };
        } else if (progressPercent <= 75) {
          newSteps[1] = { ...newSteps[1], status: "completed" };
          newSteps[2] = { ...newSteps[2], status: "in-progress" };
        } else if (progressPercent < 100) {
          newSteps[1] = { ...newSteps[1], status: "completed" };
          newSteps[2] = { ...newSteps[2], status: "completed" };
          newSteps[3] = { ...newSteps[3], status: "in-progress" };
        }
      } else if (status === "completed") {
        newSteps.forEach((_, idx) => {
          newSteps[idx] = { ...newSteps[idx], status: "completed" };
        });
      } else if (status === "failed") {
        // Mark current step as failed, previous as completed
        const currentStepIndex = Math.min(
          Math.floor((progressPercent / 100) * newSteps.length),
          newSteps.length - 1
        );

        newSteps.forEach((_, idx) => {
          if (idx < currentStepIndex) {
            newSteps[idx] = { ...newSteps[idx], status: "completed" };
          } else if (idx === currentStepIndex) {
            newSteps[idx] = { ...newSteps[idx], status: "failed" };
          }
        });
      } else if (status === "canceled") {
        // Mark all remaining steps as pending
        const currentStepIndex = Math.min(
          Math.floor((progressPercent / 100) * newSteps.length),
          newSteps.length - 1
        );

        newSteps.forEach((_, idx) => {
          if (idx < currentStepIndex) {
            newSteps[idx] = { ...newSteps[idx], status: "completed" };
          }
        });
      }

      return newSteps;
    });
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold">Scan Progress</h3>
        <span className="text-sm text-muted">{currentProgress}%</span>
      </div>

      {/* Progress bar */}
      <div className="mb-6 h-2 bg-border rounded-full overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-500 ease-out"
          style={{ width: `${currentProgress}%` }}
        />
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              {step.status === "completed" && (
                <CheckCircle size={24} className="text-success" />
              )}
              {step.status === "in-progress" && (
                <Loader size={24} className="text-primary animate-spin" />
              )}
              {step.status === "failed" && (
                <AlertCircle size={24} className="text-destructive" />
              )}
              {step.status === "pending" && (
                <div className="w-6 h-6 rounded-full border-2 border-border" />
              )}
              {index < steps.length - 1 && (
                <div className="w-0.5 h-12 bg-border my-2" />
              )}
            </div>
            <div className="flex-1 pt-1">
              <p
                className={`font-medium ${
                  step.status === "failed" ? "text-destructive" : ""
                }`}
              >
                {step.name}
              </p>
              {step.time && (
                <p className="text-sm text-muted flex items-center gap-1 mt-1">
                  <Clock size={14} />
                  {step.time}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
