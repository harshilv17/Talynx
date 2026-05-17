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
  type?: string;
  github_profile?: any;
  response?: string;
  evaluation?: any;
  notes?: string;
  rejection_feedback?: RejectionFeedback;
}

export interface SkillGap {
  skill: string;
  importance: string;
  recommendation: string;
}

export interface RejectionFeedback {
  feedback_id: string;
  generated_at: string;
  version: number;
  strengths: string[];
  skill_gaps: SkillGap[];
  experience_gaps: string[];
  improvement_suggestions: string[];
  technologies_to_learn: string[];
  overall_summary: string;
  encouragement: string;
  email_sent: boolean;
  rag_metadata: {
    chunks_used: number;
    retrieval_scores: number[];
    embedding_model: string;
    total_chunks: number;
  };
}

export interface SourcingStatusResponse {
  thread_id: string;
  status: string;
  stage?: string;
  progress?: number;
  message?: string;
  error_message?: string | null;
  elapsed_seconds?: number;
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
