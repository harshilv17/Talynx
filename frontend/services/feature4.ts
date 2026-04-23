const API_BASE = "http://localhost:8000/api/v1/feature4";

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
