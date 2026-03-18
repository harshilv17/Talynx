import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** API base URL without trailing slash (handles env var with/without slash) */
export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL || ""
  return url.replace(/\/+$/, "")
}
