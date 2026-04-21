"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CandidateCard } from "./CandidateCard";
import { Loader2, Search, Users, CheckCircle, AlertCircle } from "lucide-react";
import { getApiBaseUrl } from "@/lib/utils";
import type { SourcingStatusResponse, CandidateResult } from "@/lib/types";

interface SourcingViewProps {
  threadId: string;
}

const STEPS = [
  "Fetching published job description…",
  "Loading candidate profiles…",
  "Generating semantic embeddings…",
  "Ranking and Filtering candidates by relevance…",
  "Preparing the initial pipeline…",
];

export function SourcingView({ threadId }: SourcingViewProps) {
  const [status, setStatus] = useState<SourcingStatusResponse | null>(null);
  const [candidates, setCandidates] = useState<CandidateResult[]>([]);
  const [activeTab, setActiveTab] = useState<string>("pending");
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stepIndex, setStepIndex] = useState(0);

  const fetchCandidates = useCallback(async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/feature2/candidates?job_id=${threadId}`);
      if (response.ok) {
        const data = await response.json();
        setCandidates(data.candidates || []);
      }
    } catch (e) {
      console.error("Failed to fetch candidates", e);
    }
  }, [threadId]);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/feature2/status/${threadId}`
      );
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to fetch sourcing status");
      }
      const data: SourcingStatusResponse = await response.json();
      setStatus(data);
      if (data.status === "completed") {
        fetchCandidates();
      }
      return data;
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [threadId, fetchCandidates]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (status?.status === "in_progress") {
      const interval = setInterval(fetchStatus, 2500);
      return () => clearInterval(interval);
    }
  }, [status?.status, fetchStatus]);

  useEffect(() => {
    if (status?.status === "in_progress") {
      const interval = setInterval(() => {
        setStepIndex((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
      }, 3000);
      return () => clearInterval(interval);
    } else {
      setStepIndex(0);
    }
  }, [status?.status]);

  const handleStartSourcing = async () => {
    setIsStarting(true);
    setError(null);

    try {
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/feature2/start-sourcing/${threadId}`,
        { method: "POST" }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to start sourcing");
      }

      setStatus({ thread_id: threadId, status: "in_progress", error_message: null });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsStarting(false);
    }
  };

  const handleCandidateAction = async (candidateId: string, action: string) => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/feature2/candidate/${candidateId}/${action}`, {
        method: "POST"
      });
      if (!response.ok) throw new Error("Failed to update candidate");
      
      const data = await response.json();
      
      // Update local state
      setCandidates(prev => 
        prev.map(c => c.id === candidateId ? { ...c, status: data.new_status } : c)
      );
    } catch (e) {
      console.error(e);
      alert("Failed to update candidate status");
    }
  };

  const filteredCandidates = candidates.filter(c => c.status === activeTab);

  if (status?.status === "completed") {
    if (!candidates || candidates.length === 0) {
      return (
        <div className="max-w-2xl mx-auto py-12">
          <Card className="shadow-lg">
            <CardContent className="pt-6 space-y-6 text-center">
              <div className="flex justify-center">
                <div className="rounded-full bg-yellow-100 p-6">
                  <Users className="h-16 w-16 text-yellow-600" />
                </div>
              </div>
              <div className="space-y-2">
                <h1 className="text-3xl font-bold">No Candidates Found</h1>
                <p className="text-slate-600">
                  No suitable candidates found for this role. Try adjusting the job description and sourcing again.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    const counts = {
      pending: candidates.filter(c => c.status === "pending").length,
      shortlisted: candidates.filter(c => c.status === "shortlisted").length,
      saved: candidates.filter(c => c.status === "saved").length,
      rejected: candidates.filter(c => c.status === "rejected").length,
    };

    return (
      <div className="max-w-4xl mx-auto space-y-6 mb-12">
        <div className="text-center space-y-2 mb-8">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-green-100 p-4">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Sourcing Complete</h1>
          <p className="text-slate-600">
            {candidates.length} candidates matched and screened against your job description
          </p>
        </div>

        {/* Custom Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8 border-b pb-4">
          <Button 
            variant={activeTab === "pending" ? "default" : "outline"} 
            className="rounded-full" 
            onClick={() => setActiveTab("pending")}
          >
            Pending Review ({counts.pending})
          </Button>
          <Button 
            variant={activeTab === "shortlisted" ? "default" : "outline"} 
            className="rounded-full"
            onClick={() => setActiveTab("shortlisted")}
          >
            Shortlisted ({counts.shortlisted})
          </Button>
          <Button 
            variant={activeTab === "saved" ? "default" : "outline"} 
            className="rounded-full"
            onClick={() => setActiveTab("saved")}
          >
            Saved ({counts.saved})
          </Button>
          <Button 
            variant={activeTab === "rejected" ? "default" : "outline"} 
            className="rounded-full"
            onClick={() => setActiveTab("rejected")}
          >
            Rejected ({counts.rejected})
          </Button>
        </div>

        {filteredCandidates.length === 0 ? (
          <div className="text-center p-12 border border-dashed rounded-lg bg-slate-50 text-slate-500">
            No candidates found in this category.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-stretch">
            {filteredCandidates.map((candidate, index) => (
              <CandidateCard
                key={candidate.id}
                candidate={candidate}
                rank={index + 1}
                onAction={handleCandidateAction}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  if (status?.status === "in_progress") {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="shadow-lg">
          <CardContent className="py-12">
            <div className="flex flex-col items-center justify-center space-y-6">
              <div className="relative">
                <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" style={{ animationDuration: "2s" }} />
                <div className="relative rounded-full bg-primary/10 p-6">
                  <Search className="h-12 w-12 text-primary animate-pulse" />
                </div>
              </div>

              <div className="text-center space-y-2">
                <h2 className="text-xl font-semibold">Sourcing Candidates…</h2>
                <p className="text-slate-600 text-center max-w-md">
                  {STEPS[stepIndex]}
                </p>
              </div>

              <div className="w-full max-w-xs space-y-2">
                {STEPS.map((step, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    {i < stepIndex ? (
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                    ) : i === stepIndex ? (
                      <Loader2 className="h-4 w-4 text-primary animate-spin flex-shrink-0" />
                    ) : (
                      <div className="h-4 w-4 rounded-full border-2 border-slate-200 flex-shrink-0" />
                    )}
                    <span className={i <= stepIndex ? "text-slate-900" : "text-slate-400"}>
                      {step.replace("…", "")}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <Card className="shadow-lg">
        <CardContent className="pt-6 space-y-6 text-center">
          <div className="flex justify-center">
            <div className="rounded-full bg-blue-100 p-6">
              <Users className="h-16 w-16 text-blue-600" />
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Sourcing & Screening</h1>
            <p className="text-slate-600">
              Find and rank the best candidates for your published job description using AI-powered semantic matching.
            </p>
          </div>

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-destructive" />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            </div>
          )}

          <div className="pt-2">
            <Button
              size="lg"
              onClick={handleStartSourcing}
              disabled={isStarting}
              className="px-8"
              id="start-sourcing-btn"
            >
              {isStarting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting…
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Start Sourcing
                </>
              )}
            </Button>
          </div>

          <p className="text-xs text-muted-foreground">
            This will scan candidate profiles and rank them against your job description
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
