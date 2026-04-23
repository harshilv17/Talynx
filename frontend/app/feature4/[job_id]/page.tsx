"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle } from "lucide-react";
import { EvaluationCandidate, fetchEvaluations } from "../../../services/feature4";
import { CandidateCard } from "../../../components/feature4/CandidateCard";

export default function EvaluationDashboard() {
  const params = useParams();
  const job_id = params?.job_id as string;

  const [candidates, setCandidates] = useState<EvaluationCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!job_id) return;

    const loadData = async () => {
      try {
        const data = await fetchEvaluations(job_id);
        setCandidates(data);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [job_id]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 p-6">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-200 flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (candidates.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-500">
        <p>No candidates available for evaluation.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 text-gray-900 dark:text-gray-100">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold mb-8">Candidate Evaluations</h1>
        
        <div className="space-y-4">
          {candidates.map((candidate) => (
            <CandidateCard key={candidate.id} candidate={candidate} />
          ))}
        </div>
      </div>
    </div>
  );
}
