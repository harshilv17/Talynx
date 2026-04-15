"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CandidateResult } from "@/lib/types";

interface CandidateCardProps {
  candidate: CandidateResult;
  rank: number;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "bg-green-100 text-green-800 border-green-200";
  if (score >= 60) return "bg-yellow-100 text-yellow-800 border-yellow-200";
  return "bg-red-100 text-red-800 border-red-200";
}

function getScoreBg(score: number): string {
  if (score >= 80) return "from-green-50 to-emerald-50 border-green-200";
  if (score >= 60) return "from-yellow-50 to-amber-50 border-yellow-200";
  return "from-red-50 to-orange-50 border-red-200";
}

export function CandidateCard({ candidate, rank }: CandidateCardProps) {
  return (
    <Card className={`shadow-md hover:shadow-lg transition-all duration-200 bg-gradient-to-br ${getScoreBg(candidate.match_score)}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
              {rank}
            </div>
            <CardTitle className="text-lg">{candidate.name}</CardTitle>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-bold border ${getScoreColor(candidate.match_score)}`}>
            {candidate.match_score}%
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          <span>{candidate.experience} years experience</span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {candidate.skills.map((skill) => (
            <Badge key={skill} variant="secondary" className="text-xs">
              {skill}
            </Badge>
          ))}
        </div>

        <p className="text-sm text-slate-600 leading-relaxed line-clamp-3">
          {candidate.resume_text}
        </p>
      </CardContent>
    </Card>
  );
}
