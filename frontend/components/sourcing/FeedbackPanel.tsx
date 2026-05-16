"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  generateFeedback,
  fetchFeedback,
  regenerateFeedback,
  sendFeedbackEmail,
} from "@/services/feature4";
import type { RejectionFeedback } from "@/lib/types";

interface FeedbackPanelProps {
  candidateId: string;
  candidateName: string;
  existingFeedback?: RejectionFeedback | null;
  onFeedbackGenerated?: (feedback: RejectionFeedback) => void;
}

export function FeedbackPanel({
  candidateId,
  candidateName,
  existingFeedback,
  onFeedbackGenerated,
}: FeedbackPanelProps) {
  const [feedback, setFeedback] = useState<RejectionFeedback | null>(
    existingFeedback || null
  );
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = feedback
        ? await regenerateFeedback(candidateId)
        : await generateFeedback(candidateId);
      setFeedback(res.feedback);
      onFeedbackGenerated?.(res.feedback);
      setSuccessMsg(feedback ? "Feedback regenerated (v" + res.feedback.version + ")" : "Feedback generated!");
    } catch (e: any) {
      setError(e.message || "Failed to generate feedback");
    } finally {
      setLoading(false);
      setTimeout(() => setSuccessMsg(null), 3000);
    }
  };

  const handleSendEmail = async () => {
    setSending(true);
    setError(null);
    try {
      await sendFeedbackEmail(candidateId);
      setFeedback((prev) =>
        prev ? { ...prev, email_sent: true } : prev
      );
      setSuccessMsg("Feedback email sent!");
    } catch (e: any) {
      setError(e.message || "Failed to send email");
    } finally {
      setSending(false);
      setTimeout(() => setSuccessMsg(null), 3000);
    }
  };

  if (!feedback) {
    return (
      <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-amber-800">
              AI Rejection Feedback
            </p>
            <p className="text-xs text-amber-600 mt-0.5">
              Generate personalized, constructive feedback for {candidateName}
            </p>
          </div>
          <Button
            size="sm"
            onClick={handleGenerate}
            disabled={loading}
            className="bg-amber-600 hover:bg-amber-700 text-white text-xs"
          >
            {loading ? (
              <span className="flex items-center gap-1">
                <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </span>
            ) : (
              "✨ Generate AI Feedback"
            )}
          </Button>
        </div>
        {error && (
          <p className="text-xs text-red-600 mt-2">⚠ {error}</p>
        )}
      </div>
    );
  }

  return (
    <div className="mt-3 p-4 bg-gradient-to-br from-violet-50 to-indigo-50 border border-violet-200 rounded-lg space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-violet-800">
            AI Rejection Feedback
          </span>
          <Badge variant="outline" className="text-[10px] border-violet-300 text-violet-600">
            v{feedback.version}
          </Badge>
          {feedback.email_sent && (
            <Badge className="bg-green-100 text-green-700 text-[10px] border-green-200">
              ✉ Sent
            </Badge>
          )}
        </div>
        <div className="flex gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleGenerate}
            disabled={loading}
            className="h-7 px-2 text-xs text-violet-600 hover:bg-violet-100"
          >
            {loading ? "Regenerating..." : "↻ Regenerate"}
          </Button>
          {!feedback.email_sent && (
            <Button
              size="sm"
              onClick={handleSendEmail}
              disabled={sending}
              className="h-7 px-2 text-xs bg-violet-600 hover:bg-violet-700 text-white"
            >
              {sending ? "Sending..." : "✉ Send Email"}
            </Button>
          )}
        </div>
      </div>

      {/* Success/Error messages */}
      {successMsg && (
        <p className="text-xs text-green-700 bg-green-50 px-2 py-1 rounded">✅ {successMsg}</p>
      )}
      {error && (
        <p className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">⚠ {error}</p>
      )}

      {/* Summary */}
      <p className="text-sm text-slate-700 leading-relaxed">
        {feedback.overall_summary}
      </p>

      {/* Strengths */}
      {feedback.strengths.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-green-700 mb-1">✔ Strengths</p>
          <ul className="space-y-0.5">
            {feedback.strengths.map((s, i) => (
              <li key={i} className="text-xs text-slate-600 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-green-500">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Skill Gaps */}
      {feedback.skill_gaps.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-orange-700 mb-1">⚠ Skill Gaps</p>
          {feedback.skill_gaps.map((gap, i) => (
            <div key={i} className="mb-1.5 pl-3">
              <div className="text-xs font-medium text-slate-700 flex items-center">
                {gap.skill}
                <Badge variant="outline" className="ml-1 text-[9px] h-4">
                  {gap.importance}
                </Badge>
              </div>
              <p className="text-xs text-slate-500">{gap.recommendation}</p>
            </div>
          ))}
        </div>
      )}

      {/* Improvement Suggestions */}
      {feedback.improvement_suggestions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-blue-700 mb-1">💡 Suggestions</p>
          <ul className="space-y-0.5">
            {feedback.improvement_suggestions.map((s, i) => (
              <li key={i} className="text-xs text-slate-600 pl-3 relative before:content-['→'] before:absolute before:left-0 before:text-blue-400">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Technologies to Learn */}
      {feedback.technologies_to_learn.length > 0 && (
        <div className="flex items-center gap-1 flex-wrap">
          <span className="text-xs font-semibold text-slate-600">Learn:</span>
          {feedback.technologies_to_learn.map((t) => (
            <Badge key={t} variant="secondary" className="text-[10px] h-5">
              {t}
            </Badge>
          ))}
        </div>
      )}

      {/* Encouragement */}
      {feedback.encouragement && (
        <p className="text-xs text-violet-700 italic border-l-2 border-violet-300 pl-2">
          {feedback.encouragement}
        </p>
      )}

      {/* RAG Metadata (collapsed) */}
      <details className="text-[10px] text-slate-400">
        <summary className="cursor-pointer hover:text-slate-500">RAG metadata</summary>
        <p className="mt-1">
          Chunks: {feedback.rag_metadata.chunks_used}/{feedback.rag_metadata.total_chunks} |
          Model: {feedback.rag_metadata.embedding_model} |
          Scores: [{feedback.rag_metadata.retrieval_scores.map(s => s.toFixed(3)).join(", ")}]
        </p>
      </details>
    </div>
  );
}
