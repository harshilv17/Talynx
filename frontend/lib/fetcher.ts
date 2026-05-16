import { getApiBaseUrl } from "./utils";

export async function fetchWithRetry(
  endpoint: string,
  options: RequestInit = {},
  retries = 2
) {
  const baseUrl = getApiBaseUrl();
  // Ensure the endpoint starts with a slash
  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${normalizedEndpoint}`;

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }

      // Handle 204 No Content or empty responses
      if (response.status === 204) return null;
      
      return await response.json();
    } catch (err) {
      if (i === retries) {
        console.error(`[API Fetch Error] Failed after ${retries} retries:`, err);
        throw err;
      }
      // Exponential backoff
      await new Promise((res) => setTimeout(res, 1000 * (i + 1)));
    }
  }
}
