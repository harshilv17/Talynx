"use client";

import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { CandidateResult } from "@/lib/types";

interface CandidateCardProps {
  candidate: CandidateResult;
  rank: number;
  onAction?: (candidateId: string, action: string) => void;
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

function getStatusBadge(status: string) {
  switch (status.toLowerCase()) {
    case 'shortlisted': return <Badge variant="default" className="bg-green-600 hover:bg-green-700">Shortlisted</Badge>;
    case 'rejected': return <Badge variant="destructive">Rejected</Badge>;
    case 'saved': return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Saved</Badge>;
    default: return <Badge variant="outline" className="text-slate-500">Pending</Badge>;
  }
}

export function CandidateCard({ candidate, rank, onAction }: CandidateCardProps) {
  return (
    <Card className={`shadow-md hover:shadow-lg transition-all duration-200 bg-gradient-to-br ${getScoreBg(candidate.score)} flex flex-col`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
              {rank}
            </div>
            <div className="flex flex-col">
                <CardTitle className="text-lg">{candidate.name}</CardTitle>
                <div className="mt-1 flex items-center gap-2">
                  {getStatusBadge(candidate.status)}
                  {candidate.source === 'demo' ? (
                    <Badge variant="outline" className="bg-slate-100 text-slate-600 border-slate-200">Demo</Badge>
                  ) : (
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">Live</Badge>
                  )}
                </div>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-bold border ${getScoreColor(candidate.score)}`}>
            {candidate.score}%
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 flex-1">
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

        {candidate.status === 'rejected' && candidate.rejection_reason && (
          <div className="mt-2 p-2 bg-red-50 border border-red-100 rounded-md text-xs text-red-800">
            <strong>Rejection Reason:</strong> {candidate.rejection_reason}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between items-center pt-2 pb-4 px-6 border-t border-slate-100/50">
        <Button 
            variant="outline" 
            size="sm" 
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={() => onAction?.(candidate.id, 'reject')}
            disabled={candidate.status === 'rejected'}
        >
            Reject
        </Button>
        <div className="flex gap-2">
            <Button 
                variant="outline" 
                size="sm"
                onClick={() => onAction?.(candidate.id, 'save')}
                disabled={candidate.status === 'saved'}
            >
                Save
            </Button>
            <Button 
                size="sm" 
                className="bg-primary"
                onClick={() => onAction?.(candidate.id, 'shortlist')}
                disabled={candidate.status === 'shortlisted'}
            >
                Shortlist
            </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
