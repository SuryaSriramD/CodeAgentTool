"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw, Home } from "lucide-react";
import Link from "next/link";

interface ErrorDisplayProps {
  error?: Error | null;
  title?: string;
  message?: string;
  onRetry?: () => void;
  showHomeButton?: boolean;
}

export function ErrorDisplay({
  error,
  title = "Something went wrong",
  message,
  onRetry,
  showHomeButton = true,
}: ErrorDisplayProps) {
  const displayMessage =
    message ||
    error?.message ||
    "An unexpected error occurred. Please try again.";

  return (
    <div className="flex items-center justify-center min-h-[400px] p-6">
      <div className="max-w-md w-full space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{title}</AlertTitle>
          <AlertDescription>{displayMessage}</AlertDescription>
        </Alert>

        <div className="flex gap-2">
          {onRetry && (
            <Button onClick={onRetry} className="flex-1">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          )}
          {showHomeButton && (
            <Link href="/dashboard" className="flex-1">
              <Button variant="outline" className="w-full">
                <Home className="mr-2 h-4 w-4" />
                Go to Dashboard
              </Button>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

interface InlineErrorProps {
  error?: Error | null;
  message?: string;
  onRetry?: () => void;
}

export function InlineError({ error, message, onRetry }: InlineErrorProps) {
  const displayMessage = message || error?.message || "An error occurred";

  return (
    <Alert variant="destructive" className="my-4">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>{displayMessage}</span>
        {onRetry && (
          <Button variant="ghost" size="sm" onClick={onRetry}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}
