import { getApiBaseUrl } from "../lib/utils";

const API_BASE = `${getApiBaseUrl()}/api/v1/feature4`;

export interface EvaluationCandidate {
  id: string;
  name: string;
  score: number;
  status: string;
  evaluation: {
    technical_score: number;
    experience_score: number;
    skill_match_score: number;
    overall_score: number;
    summary: string;
  };
  decision: {
    recommendation: string;
    confidence: number;
    reason: string;
  };
}

export async function fetchEvaluations(jobId: string): Promise<EvaluationCandidate[]> {
  const res = await fetch(`${API_BASE}/evaluation/${jobId}`);
  if (!res.ok) throw new Error("Failed to load candidates");
  const data = await res.json();
  return data.candidates;
}

export async function generateOffer(candidateId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/offer/${candidateId}`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to generate offer");
  return data.offer_text;
}

// ── Rejection Feedback API ──────────────────────────────────────────────────

export async function generateFeedback(candidateId: string) {
  const res = await fetch(`${API_BASE}/feedback/${candidateId}/generate`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to generate feedback");
  return data;
}

export async function fetchFeedback(candidateId: string) {
  const res = await fetch(`${API_BASE}/feedback/${candidateId}`);
  if (res.status === 404) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch feedback");
  return data;
}

export async function regenerateFeedback(candidateId: string) {
  const res = await fetch(`${API_BASE}/feedback/${candidateId}/regenerate`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to regenerate feedback");
  return data;
}

export async function sendFeedbackEmail(candidateId: string) {
  const res = await fetch(`${API_BASE}/feedback/${candidateId}/send`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to send feedback email");
  return data;
}

// ── Bulk API ───────────────────────────────────────────────────────────────

export async function bulkGenerateFeedback(jobId: string) {
  const res = await fetch(`${API_BASE}/feedback/job/${jobId}/generate-all`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to bulk generate feedback");
  return data;
}

export async function bulkSendFeedbackEmail(jobId: string) {
  const res = await fetch(`${API_BASE}/feedback/job/${jobId}/send-all`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to bulk send feedback email");
  return data;
}

