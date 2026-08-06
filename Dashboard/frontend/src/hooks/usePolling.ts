"use client";

import { useEffect, useRef } from "react";

interface UsePollingOptions {
  enabled?: boolean;
  intervalMs?: number;
  onPoll: () => void | Promise<void>;
}

export function usePolling({
  enabled = true,
  intervalMs = 5000,
  onPoll,
}: UsePollingOptions) {
  const callbackRef = useRef(onPoll);

  useEffect(() => {
    callbackRef.current = onPoll;
  }, [onPoll]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const tick = () => {
      void callbackRef.current();
    };

    tick();
    const timer = window.setInterval(tick, intervalMs);

    return () => {
      window.clearInterval(timer);
    };
  }, [enabled, intervalMs]);
}
