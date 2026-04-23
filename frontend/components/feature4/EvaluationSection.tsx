import React from "react";
import { EvaluationCandidate } from "../../services/feature4";

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600 dark:text-gray-400">{label}</span>
        <span className="font-medium text-gray-900 dark:text-gray-100">{score}%</span>
      </div>
      <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div 
          className="h-full bg-blue-500" 
          style={{ width: `${score}%` }} 
        />
      </div>
    </div>
  );
}

export function EvaluationSection({ evaluation }: { evaluation: EvaluationCandidate['evaluation'] }) {
  return (
    <div className="space-y-4">
      <h4 className="font-medium text-sm text-gray-500 uppercase tracking-wider">Evaluation Breakdown</h4>
      
      <ScoreBar label="Technical Score" score={evaluation.technical_score} />
      <ScoreBar label="Experience Score" score={evaluation.experience_score} />
      <ScoreBar label="Skill Match Score" score={evaluation.skill_match_score} />

      <div className="pt-2">
        <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
          {evaluation.summary}
        </p>
      </div>
    </div>
  );
}
