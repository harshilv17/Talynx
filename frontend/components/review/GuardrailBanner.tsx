"use client";

import { AlertCircle, CheckCircle } from "lucide-react";

interface GuardrailBannerProps {
  passed: boolean;
  toneScore: number;
  issueCount: number;
}

export function GuardrailBanner({ passed, toneScore, issueCount }: GuardrailBannerProps) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        passed
          ? "bg-green-50 border-green-200"
          : "bg-amber-50 border-amber-200"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {passed ? (
            <CheckCircle className="h-5 w-5 text-green-600" />
          ) : (
            <AlertCircle className="h-5 w-5 text-amber-600" />
          )}
        </div>
        <div className="flex-1">
          <h3
            className={`font-semibold ${
              passed ? "text-green-900" : "text-amber-900"
            }`}
          >
            {passed ? "Guardrail Check Passed" : "Issues Found and Corrected"}
          </h3>
          <p
            className={`text-sm mt-1 ${
              passed ? "text-green-700" : "text-amber-700"
            }`}
          >
            {passed
              ? "No compliance issues detected. The job description is ready for review."
              : `${issueCount} issue${issueCount !== 1 ? "s" : ""} detected and automatically corrected.`}
          </p>
          <div className="mt-2">
            <span className="text-xs font-medium">Tone Score: </span>
            <span
              className={`text-xs font-bold ${
                toneScore >= 80
                  ? "text-green-700"
                  : toneScore >= 60
                  ? "text-amber-700"
                  : "text-red-700"
              }`}
            >
              {toneScore.toFixed(0)}/100
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
