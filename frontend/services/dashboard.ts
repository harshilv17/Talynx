import { getApiBaseUrl } from "@/lib/utils";

const API_BASE = `${getApiBaseUrl()}/api/v1/dashboard`;

export async function completePipeline(jobId: string) {
  const res = await fetch(`${API_BASE}/pipeline/${jobId}/complete`, { method: "PATCH" });
  if (!res.ok) throw new Error("Failed to complete pipeline");
  return res.json();
}

export async function archivePipeline(jobId: string) {
  const res = await fetch(`${API_BASE}/pipeline/${jobId}/archive`, { method: "PATCH" });
  if (!res.ok) throw new Error("Failed to archive pipeline");
  return res.json();
}

export async function restorePipeline(jobId: string) {
  const res = await fetch(`${API_BASE}/pipeline/${jobId}/restore`, { method: "PATCH" });
  if (!res.ok) throw new Error("Failed to restore pipeline");
  return res.json();
}

export async function deletePipeline(jobId: string) {
  const res = await fetch(`${API_BASE}/pipeline/${jobId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete pipeline");
  return res.json();
}
