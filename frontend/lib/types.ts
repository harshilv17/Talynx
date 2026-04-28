export interface JDContent {
  job_title: string;
  tagline: string;
  about_role: string;
  responsibilities: string[];
  requirements: string[];
  nice_to_haves: string[];
  company_blurb: string;
  salary_range: string;
  location_work_type: string;
}

export interface GuardrailIssue {
  issue: string;
  original_text: string;
  suggested_fix: string;
}

export interface GuardrailResult {
  passed: boolean;
  issues: GuardrailIssue[];
  corrected_jd: JDContent | null;
  tone_score: number;
}

export interface StatusResponse {
  thread_id: string;
  status: string;
  role_brief?: any;
  jd_draft: JDContent | null;
  guardrail_result: GuardrailResult | null;
  version: number;
  error_message: string | null;
}

export interface RoleBriefInput {
  role_title: string;
  team: string;
  seniority: string;
  work_type: string;
  location: string;
  must_have_skills: string[];
  nice_to_have_skills: string[];
  salary_min: number;
  salary_max: number;
  currency: string;
  headcount: number;
  years_of_experience?: number;
  reports_to?: string;
  key_outcomes?: string[];
  context_note?: string;
  tone_preference: string;
}

export interface CandidateResult {
  id: string;
  name: string;
  skills: string[];
  experience: number;
  score: number;
  status: string;
  rejection_reason?: string;
  resume_text: string;
  source?: string;
}

export interface SourcingStatusResponse {
  thread_id: string;
  status: string;
  error_message?: string | null;
}

export interface SourcingCandidatesResponse {
  job_id: string;
  candidates: CandidateResult[];
}

export interface CandidateActionResponse {
  success: boolean;
  new_status: string;
  message: string;
}
