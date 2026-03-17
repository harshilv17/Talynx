"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { JDPreview } from "./JDPreview";
import { GuardrailBanner } from "./GuardrailBanner";
import { ActionPanel } from "./ActionPanel";
import { SuccessScreen } from "./SuccessScreen";
import { Loader2 } from "lucide-react";

interface JDContent {
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

interface GuardrailResult {
  passed: boolean;
  issues: Array<{
    issue: string;
    original_text: string;
    suggested_fix: string;
  }>;
  corrected_jd: JDContent | null;
  tone_score: number;
}

interface StatusData {
  thread_id: string;
  status: string;
  jd_draft: JDContent | null;
  guardrail_result: GuardrailResult | null;
  version: number;
  error_message: string | null;
}

interface JDReviewProps {
  threadId: string;
}

export function JDReview({ threadId }: JDReviewProps) {
  const router = useRouter();
  const [status, setStatus] = useState<StatusData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedJd, setEditedJd] = useState<JDContent | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/status/${threadId}`
        );
        
        if (!response.ok) {
          throw new Error("Failed to fetch status");
        }

        const data: StatusData = await response.json();
        setStatus(data);

        if (data.jd_draft && !editedJd) {
          setEditedJd(data.jd_draft);
        }

        if (data.status === "pending_review" || data.status === "published" || data.status === "failed") {
          setIsLoading(false);
        }
      } catch (err: any) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    fetchStatus();

    if (!status || (status.status !== "pending_review" && status.status !== "published" && status.status !== "failed")) {
      const interval = setInterval(fetchStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [threadId, status?.status]);

  const handleApprove = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/review/${threadId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "approve",
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to approve");
      }

      const interval = setInterval(async () => {
        const statusResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/status/${threadId}`
        );
        const statusData = await statusResponse.json();
        
        if (statusData.status === "published") {
          clearInterval(interval);
          setStatus(statusData);
          setIsSubmitting(false);
        }
      }, 2000);
    } catch (err: any) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  const handleEditSave = async () => {
    if (!editedJd) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/review/${threadId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "edit",
            edited_jd: editedJd,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save edits");
      }

      const interval = setInterval(async () => {
        const statusResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/status/${threadId}`
        );
        const statusData = await statusResponse.json();
        
        if (statusData.status === "published") {
          clearInterval(interval);
          setStatus(statusData);
          setIsSubmitting(false);
          setIsEditing(false);
        }
      }, 2000);
    } catch (err: any) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  const handleRevise = async (feedback: string) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/feature1/review/${threadId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "revise",
            feedback: feedback,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to request revision");
      }

      setIsLoading(true);
      setIsSubmitting(false);
    } catch (err: any) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  const handleEdit = () => {
    if (isEditing) {
      handleEditSave();
    } else {
      setIsEditing(true);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <Card className="shadow-lg">
          <CardContent className="py-12">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
              <h2 className="text-xl font-semibold">Generating job description...</h2>
              <p className="text-slate-600 text-center max-w-md">
                Our AI is crafting a professional, bias-free job description based on your requirements.
                This usually takes 30-60 seconds.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status?.status === "published") {
    return <SuccessScreen />;
  }

  if (status?.status === "failed") {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="shadow-lg border-destructive">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <h2 className="text-2xl font-bold text-destructive">Generation Failed</h2>
              <p className="text-slate-700">{status.error_message || "An unknown error occurred"}</p>
              <Button onClick={() => router.push("/new-role")}>
                Start Over
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!status?.jd_draft || !status?.guardrail_result) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <Card className="shadow-lg">
          <CardContent className="py-12 text-center">
            <p className="text-slate-600">No job description available yet</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Review Job Description</h1>
        <p className="text-slate-600 mt-1">
          Review the AI-generated job description and choose how to proceed
        </p>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4 mb-6">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <GuardrailBanner
            passed={status.guardrail_result.passed}
            toneScore={status.guardrail_result.tone_score}
            issueCount={status.guardrail_result.issues.length}
          />

          <JDPreview
            jd={status.jd_draft}
            isEditing={isEditing}
            editedJd={editedJd || status.jd_draft}
            onJdChange={setEditedJd}
          />
        </div>

        <div className="lg:col-span-1">
          <ActionPanel
            onApprove={handleApprove}
            onEdit={handleEdit}
            onRevise={handleRevise}
            isSubmitting={isSubmitting}
            isEditing={isEditing}
            revisionNumber={status.version - 1}
          />
        </div>
      </div>
    </div>
  );
}
