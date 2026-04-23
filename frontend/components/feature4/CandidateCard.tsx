import React, { useState } from "react";
import { ChevronDown, ChevronUp, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { EvaluationCandidate } from "../../services/feature4";
import { EvaluationSection } from "./EvaluationSection";
import { DecisionSection } from "./DecisionSection";

export function CandidateCard({ candidate }: { candidate: EvaluationCandidate }) {
  const [expanded, setExpanded] = useState(false);
  const { evaluation, decision } = candidate;
  const isHire = decision.recommendation === "hire";

  const getScoreColor = (score: number) => {
    if (score >= 75) return "bg-green-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getRecommendationBadge = () => {
    if (isHire && evaluation.overall_score >= 75) {
      return <span className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-1 rounded-md text-sm font-medium"><CheckCircle2 className="h-4 w-4" /> Strong Hire</span>;
    }
    if (isHire) {
      return <span className="flex items-center gap-1 text-yellow-600 bg-yellow-50 px-2 py-1 rounded-md text-sm font-medium"><AlertCircle className="h-4 w-4" /> Moderate Hire</span>;
    }
    return <span className="flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded-md text-sm font-medium"><XCircle className="h-4 w-4" /> No Hire</span>;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-all">
      {/* Header / Summary Row */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className="p-5 flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750"
      >
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 flex-1">
          <div className="min-w-[200px]">
            <h3 className="font-semibold text-lg">{candidate.name}</h3>
            <span className="text-xs text-gray-500 uppercase tracking-wide">{candidate.status}</span>
          </div>

          <div className="flex-1 max-w-xs">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">Overall Score</span>
              <span className="font-medium">{evaluation.overall_score}%</span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getScoreColor(evaluation.overall_score)}`} 
                style={{ width: `${evaluation.overall_score}%` }} 
              />
            </div>
          </div>

          <div className="flex items-center gap-4 ml-auto">
            {getRecommendationBadge()}
            {expanded ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="p-5 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <EvaluationSection evaluation={evaluation} />
            <DecisionSection candidate={candidate} />
          </div>
        </div>
      )}
    </div>
  );
}
