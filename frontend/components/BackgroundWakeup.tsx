"use client";

import { useEffect } from "react";
import { getApiBaseUrl } from "@/lib/utils";

export function BackgroundWakeup() {
  useEffect(() => {
    // Ping the backend system status to wake up Render.
    // Timeout is 45s because Render cold starts can take up to 30s-40s.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000);

    fetch(`${getApiBaseUrl()}/api/v1/system/status`, { 
      cache: 'no-store',
      signal: controller.signal 
    })
    .then(res => console.log("[BackgroundWakeup] Backend is awake! Status:", res.status))
    .catch((err) => {
      console.log("[BackgroundWakeup] Silent ping complete or aborted:", err.name);
    })
    .finally(() => {
      clearTimeout(timeoutId);
    });
  }, []);

  return null;
}
