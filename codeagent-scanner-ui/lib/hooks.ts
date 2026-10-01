"use client";
import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { capabilities, job } from "./api-client";
import { TERMINAL, type RunEvent } from "./types";

export function useCapabilities() {
  return useQuery({ queryKey: ["capabilities"], queryFn: capabilities, refetchInterval: 15000 });
}
export function useRun(id: string | null | undefined) {
  return useQuery({ queryKey: ["job", id], queryFn: () => job(id!), enabled: Boolean(id),
    refetchInterval: (query) => query.state.data && TERMINAL.includes(query.state.data.status) ? 15000 : 4000 });
}
// A single subscription is owned by the run page. Other components consume its
// shared query cache and events, rather than opening their own EventSources.
export function useRunEvents(id: string, enabled = true, finished = false) {
  const client = useQueryClient();
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const finishedRef = useRef(finished);
  finishedRef.current = finished;
  useEffect(() => {
    setEvents([]);
    if (!enabled) return;
    const stream = new EventSource(`/api/backend/events/${encodeURIComponent(id)}`);
    let invalidateTimer: ReturnType<typeof setTimeout> | undefined;
    const receive = (event: MessageEvent) => {
      setConnected(true);
      try {
        const payload = JSON.parse(event.data) as RunEvent;
        if (typeof payload.seq === "number") {
          setEvents((previous) => previous.some((item) => item.seq === payload.seq && item.job_id === payload.job_id) ? previous : [...previous, payload].slice(-200));
        }
      } catch { /* A malformed notification cannot replace the authoritative snapshot. */ }
      clearTimeout(invalidateTimer);
      invalidateTimer = setTimeout(() => {
        void client.invalidateQueries({ queryKey: ["job"] });
        void client.invalidateQueries({ queryKey: ["report", id] });
        void client.invalidateQueries({ queryKey: ["enhanced", id] });
        void client.invalidateQueries({ queryKey: ["jobs"] });
      }, 100);
    };
    stream.onopen = () => setConnected(true);
    stream.onerror = () => {
      setConnected(false);
      if (finishedRef.current) stream.close();
    };
    stream.onmessage = receive;
    stream.addEventListener("update", receive as EventListener);
    stream.addEventListener("snapshot", receive as EventListener);
    return () => { clearTimeout(invalidateTimer); stream.close(); setConnected(false); };
  }, [client, id, enabled]);
  return { events, connected };
}
