"use client";

import { useEffect, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { WifiOff, Wifi } from "lucide-react";
import { checkAPIConnection } from "@/lib/api-client";

export function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    // Check initial connection
    const checkConnection = async () => {
      const connected = await checkAPIConnection();
      setIsOnline(connected);
      if (!connected) {
        setShowOfflineMessage(true);
      }
    };

    checkConnection();

    // Monitor online/offline events
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineMessage(false);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineMessage(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Periodic connection check
    const interval = setInterval(async () => {
      const connected = await checkAPIConnection();
      if (!connected && isOnline) {
        setIsOnline(false);
        setShowOfflineMessage(true);
      } else if (connected && !isOnline) {
        setIsOnline(true);
        setShowOfflineMessage(false);
      }
    }, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      clearInterval(interval);
    };
  }, [isOnline]);

  if (!showOfflineMessage) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <Alert variant={isOnline ? "default" : "destructive"}>
        {isOnline ? (
          <Wifi className="h-4 w-4" />
        ) : (
          <WifiOff className="h-4 w-4" />
        )}
        <AlertDescription>
          {isOnline
            ? "Connection restored"
            : "No connection to server. Please check if the backend is running."}
        </AlertDescription>
      </Alert>
    </div>
  );
}
