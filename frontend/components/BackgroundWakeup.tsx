"use client";

import { useEffect } from "react";
import { getApiBaseUrl } from "@/lib/utils";

export function BackgroundWakeup() {
  useEffect(() => {
    // Silently ping the backend health endpoint to wake up the Render service
    // We use a short timeout so it doesn't block or hang resources unnecessarily
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    fetch(`${getApiBaseUrl()}/health`, { 
      cache: 'no-store',
      signal: controller.signal 
    })
    .catch(() => {
      // Silently ignore errors - this is just a wake-up ping
    })
    .finally(() => {
      clearTimeout(timeoutId);
    });
  }, []);

  return null;
}
