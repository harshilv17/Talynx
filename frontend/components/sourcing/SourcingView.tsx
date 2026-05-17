"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CandidateCard } from "./CandidateCard";
import { useRouter } from "next/navigation";
import { Loader2, Search, Users, CheckCircle, AlertCircle, BarChart2 } from "lucide-react";
import { getApiBaseUrl } from "@/lib/utils";
import type { SourcingStatusResponse, CandidateResult } from "@/lib/types";
import { bulkGenerateFeedback, bulkSendFeedbackEmail } from "@/services/feature4";

interface SourcingViewProps {
  threadId: string;
}

// Real-time backend tracking used instead of fake steps.

export function SourcingView({ threadId }: SourcingViewProps) {
  const router = useRouter();
  const [status, setStatus] = useState<SourcingStatusResponse | null>(null);
  const [candidates, setCandidates] = useState<CandidateResult[]>([]);
  const [activeTab, setActiveTab] = useState<string>("pending");
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stepIndex, setStepIndex] = useState(0); // Kept for legacy fallback if needed
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateResult | null>(null);
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<Set<string>>(new Set());
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [isWakingBackend, setIsWakingBackend] = useState(false);

  const [isBulkGenerating, setIsBulkGenerating] = useState(false);
  const [isBulkSending, setIsBulkSending] = useState(false);
  const [bulkStats, setBulkStats] = useState<{ processed: number, success: number, fail: number, msg?: string } | null>(null);

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
      const controller = new AbortController();
      // Render cold starts take ~30s. We use 45s to be extremely safe, preventing AbortErrors 
      // from firing before Render actually completes booting.
      const timeoutId = setTimeout(() => controller.abort(), 45000);

      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/feature2/status/${threadId}`,
        { signal: controller.signal }
      );
      clearTimeout(timeoutId);

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to fetch sourcing status");
      }
      setIsWakingBackend(false); // Successfully connected
      const data: SourcingStatusResponse = await response.json();
      setStatus(data);
      if (data.status === "completed") {
        fetchCandidates();
      } else if (data.status === "failed") {
        setError(data.error_message || "Pipeline execution failed.");
      }
      return data;
    } catch (err: any) {
      if (err.name === 'AbortError' || err.message.includes('fetch')) {
        setIsWakingBackend(true);
      } else {
        setError(err.message);
        setStatus(prev => prev ? { ...prev, status: "failed" } : null);
      }
      console.error("[Sourcing Poll Failed]", err);
      return null;
    }
  }, [threadId, fetchCandidates]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (status?.status === "in_progress") {
      const interval = setInterval(fetchStatus, 3000); // 3s polling for real-time progress
      return () => clearInterval(interval);
    }
  }, [status?.status, fetchStatus]);

  const handleStartSourcing = async () => {
    setIsStarting(true);
    setError(null);
    setIsWakingBackend(false);

    const wakeTimer = setTimeout(() => {
      setIsWakingBackend(true);
    }, 6000); // 6 seconds before showing wake up message

    try {
      const controller = new AbortController();
      // Allow 60s for the initial POST request, since if Render is cold-starting,
      // it will hold the request open until it boots. 
      // If we timeout too early, the frontend gives up while the backend is still trying to start!
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/feature2/start-sourcing/${threadId}`,
        { 
          method: "POST",
          signal: controller.signal 
        }
      );
      clearTimeout(timeoutId);
      clearTimeout(wakeTimer);

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to start sourcing");
      }

      setIsWakingBackend(false);
      setStatus({ thread_id: threadId, status: "in_progress", error_message: null });
    } catch (err: any) {
      clearTimeout(wakeTimer);
      if (err.message.includes('fetch')) {
        setIsWakingBackend(true);
      } else {
        setError(err.message);
      }
    } finally {
      setIsStarting(false);
    }
  };

  const handleCandidateAction = async (candidateId: string, action: string) => {
    try {
      let statusPayload = action;
      if (action === "shortlist") statusPayload = "shortlisted";
      if (action === "save") statusPayload = "saved";
      if (action === "reject") statusPayload = "rejected";

      console.log("[DEBUG] Payload:", { status: statusPayload });

      const response = await fetch(`${getApiBaseUrl()}/api/v1/feature2/candidate/${candidateId}/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ status: statusPayload })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update candidate");
      }
      
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

  const handleComplete = async () => {
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature2/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: threadId })
      });
      if (!res.ok) throw new Error("Failed to complete sourcing");
      const data = await res.json();
      router.push(data.next);
    } catch (e) {
      console.error(e);
      alert("Error proceeding to outreach");
    }
  };

  const filteredCandidates = candidates.filter(c => c.status === activeTab);

  const handleSaveNotes = async (candidateId: string, notes: string) => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/feature2/candidate/${candidateId}/notes`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes })
      });
      if (!response.ok) {
        throw new Error("Failed to save notes");
      }
      setCandidates(prev => prev.map(c => c.id === candidateId ? { ...c, notes } : c));
    } catch (e) {
      console.error(e);
      alert("Failed to save notes");
    }
  };

  const handleToggleSelect = (candidateId: string, selected: boolean) => {
    setSelectedCandidateIds(prev => {
      const next = new Set(prev);
      if (selected) next.add(candidateId);
      else next.delete(candidateId);
      return next;
    });
  };

  const compareCandidatesList = candidates.filter(c => selectedCandidateIds.has(c.id));
  const topCompareCandidate = compareCandidatesList.length > 0 
    ? [...compareCandidatesList].sort((a, b) => b.score - a.score)[0] 
    : null;

  const handleBulkGenerate = async () => {
    setIsBulkGenerating(true);
    setBulkStats(null);
    try {
      const res = await bulkGenerateFeedback(threadId);
      setBulkStats({
        processed: res.total_processed,
        success: res.success_count,
        fail: res.failure_count,
        msg: `Generated feedback for ${res.success_count} candidates.`
      });
      fetchCandidates(); // Refresh to show generated feedback
    } catch (e: any) {
      setBulkStats({ processed: 0, success: 0, fail: 0, msg: e.message || "Bulk generation failed" });
    } finally {
      setIsBulkGenerating(false);
      setTimeout(() => setBulkStats(null), 5000);
    }
  };

  const handleBulkSend = async () => {
    setIsBulkSending(true);
    setBulkStats(null);
    try {
      const res = await bulkSendFeedbackEmail(threadId);
      setBulkStats({
        processed: res.total_processed,
        success: res.success_count,
        fail: res.failure_count,
        msg: `Sent emails to ${res.success_count} candidates.`
      });
      fetchCandidates(); // Refresh to show email_sent status
    } catch (e: any) {
      setBulkStats({ processed: 0, success: 0, fail: 0, msg: e.message || "Bulk send failed" });
    } finally {
      setIsBulkSending(false);
      setTimeout(() => setBulkStats(null), 5000);
    }
  };

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

        {/* Custom Tabs and Proceed Button */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 border-b pb-4">
          <div className="flex flex-wrap items-center gap-2">
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
          
          <div className="flex gap-2 w-full md:w-auto">
            <Button 
              variant="secondary"
              onClick={() => setIsCompareModalOpen(true)}
              disabled={selectedCandidateIds.size < 2}
              className="flex-1 md:flex-none"
            >
              <BarChart2 className="w-4 h-4 mr-2" />
              Compare ({selectedCandidateIds.size})
            </Button>
            <Button 
              onClick={handleComplete} 
              disabled={counts.shortlisted === 0}
              className="flex-1 md:flex-none"
            >
              Proceed to Outreach &rarr;
            </Button>
          </div>
        </div>

        {activeTab === "rejected" && counts.rejected > 0 && (
          <div className="mb-6 p-4 bg-violet-50 border border-violet-200 rounded-lg flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-semibold text-violet-800">Bulk Rejection Feedback</h3>
              <p className="text-sm text-violet-600">Generate or send AI feedback for all rejected candidates at once.</p>
              {bulkStats && (
                <p className="text-xs font-medium mt-1 text-slate-700">
                  {bulkStats.msg} ({bulkStats.success} succeeded, {bulkStats.fail} failed)
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handleBulkGenerate} 
                disabled={isBulkGenerating || isBulkSending}
                className="text-violet-700 border-violet-300 hover:bg-violet-100"
              >
                {isBulkGenerating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Generate All Feedback
              </Button>
              <Button 
                onClick={handleBulkSend} 
                disabled={isBulkGenerating || isBulkSending}
                className="bg-violet-600 hover:bg-violet-700 text-white"
              >
                {isBulkSending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Send All Emails
              </Button>
            </div>
          </div>
        )}

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
                onViewResume={setSelectedCandidate}
                onSaveNotes={handleSaveNotes}
                isSelected={selectedCandidateIds.has(candidate.id)}
                onToggleSelect={handleToggleSelect}
              />
            ))}
          </div>
        )}

        {selectedCandidate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
            <Card className="w-full max-w-3xl shadow-2xl max-h-[90vh] flex flex-col">
              <div className="border-b bg-slate-50 flex flex-row items-center justify-between p-6">
                <div>
                  <h2 className="text-xl font-bold">{selectedCandidate.name} - {selectedCandidate.type === 'live' ? 'GitHub Profile' : 'Resume'}</h2>
                  <p className="text-sm text-slate-500 mt-1">
                    {selectedCandidate.experience} years experience | Match: {selectedCandidate.score}%
                  </p>
                </div>
                <Button variant="ghost" onClick={() => setSelectedCandidate(null)}>Close</Button>
              </div>
              <div className="p-6 overflow-y-auto space-y-4">
                <div>
                  <h3 className="font-semibold text-sm text-slate-700 mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCandidate.skills.map(s => (
                      <span key={s} className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded-md border border-slate-200">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
                {selectedCandidate.type === 'live' ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 bg-white p-4 rounded-md border">
                      {selectedCandidate.github_profile?.avatar_url && (
                        <img src={selectedCandidate.github_profile.avatar_url} alt="Avatar" className="w-16 h-16 rounded-full" />
                      )}
                      <div>
                        <h3 className="font-bold text-lg">{selectedCandidate.name} (@{selectedCandidate.github_profile?.username})</h3>
                        <p className="text-sm text-slate-600">{selectedCandidate.github_profile?.bio || 'No bio'}</p>
                        <div className="flex gap-4 mt-2 text-xs text-slate-500 font-medium">
                           <span>Followers: {selectedCandidate.github_profile?.followers}</span>
                           <span>Public Repos: {selectedCandidate.github_profile?.public_repos}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-sm text-slate-700 mb-2">Top Repositories</h3>
                      <div className="grid gap-3">
                        {selectedCandidate.github_profile?.top_repositories?.map((repo: any, idx: number) => (
                          <div key={idx} className="bg-white p-3 border rounded-md">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-semibold text-blue-600">{repo.name}</span>
                              <Badge variant="outline" className="text-xs bg-slate-50">★ {repo.stars}</Badge>
                            </div>
                            <p className="text-xs text-slate-600 line-clamp-2">{repo.description || "No description"}</p>
                            {repo.language && (
                              <div className="mt-2 text-xs font-medium text-slate-500 flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-blue-400"></span> {repo.language}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <h3 className="font-semibold text-sm text-slate-700 mb-2">Resume Document</h3>
                    <pre className="whitespace-pre-wrap font-sans text-slate-800 text-sm leading-relaxed border p-4 rounded-md bg-white">
                      {selectedCandidate.resume_text}
                    </pre>
                  </div>
                )}
              </div>
              <div className="p-4 border-t bg-slate-50 flex justify-end gap-2">
                 <Button onClick={() => setSelectedCandidate(null)}>Close</Button>
              </div>
            </Card>
          </div>
        )}

        {isCompareModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
            <Card className="w-full max-w-5xl shadow-2xl max-h-[90vh] flex flex-col">
              <div className="border-b bg-slate-50 flex flex-row items-center justify-between p-6">
                <div>
                  <h2 className="text-xl font-bold">Candidate Comparison</h2>
                  <p className="text-sm text-slate-500 mt-1">
                    Comparing {compareCandidatesList.length} candidates side-by-side
                  </p>
                </div>
                <Button variant="ghost" onClick={() => setIsCompareModalOpen(false)}>Close</Button>
              </div>
              <div className="p-6 overflow-x-auto overflow-y-auto flex-1">
                <table className="w-full text-left border-collapse min-w-[800px]">
                  <thead>
                    <tr className="border-b-2 border-slate-200">
                      <th className="p-3 font-semibold text-slate-700 w-1/4">Metric</th>
                      {compareCandidatesList.map(c => (
                        <th key={c.id} className="p-3 font-semibold text-slate-900 w-1/4 border-l">
                          {c.name}
                          {c.id === topCompareCandidate?.id && (
                            <Badge className="ml-2 bg-amber-500 hover:bg-amber-600">Top Match</Badge>
                          )}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-100">
                      <td className="p-3 font-medium text-slate-600 bg-slate-50">ATS Match Score</td>
                      {compareCandidatesList.map(c => (
                        <td key={c.id} className="p-3 border-l text-lg font-bold text-slate-800">
                          {c.score}%
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="p-3 font-medium text-slate-600 bg-slate-50">Experience</td>
                      {compareCandidatesList.map(c => (
                        <td key={c.id} className="p-3 border-l">
                          {c.experience} years
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="p-3 font-medium text-slate-600 bg-slate-50">Technical Score</td>
                      {compareCandidatesList.map(c => (
                        <td key={c.id} className="p-3 border-l">
                          {c.evaluation?.technical_score || c.score}%
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="p-3 font-medium text-slate-600 bg-slate-50">Overall Score</td>
                      {compareCandidatesList.map(c => (
                        <td key={c.id} className="p-3 border-l font-semibold text-primary">
                          {c.evaluation?.overall_score || c.score}%
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="p-3 font-medium text-slate-600 bg-slate-50 align-top">Skills</td>
                      {compareCandidatesList.map(c => (
                        <td key={c.id} className="p-3 border-l align-top">
                          <div className="flex flex-wrap gap-1">
                            {c.skills.map(s => (
                              <span key={s} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-md border border-slate-200">
                                {s}
                              </span>
                            ))}
                          </div>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}
      </div>
    );
  }

  if (status?.status === "in_progress") {
    // If backend isn't returning progress yet, show a fallback
    const progress = status.progress || 5; 
    const message = status.message || "Connecting to cluster...";
    
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="shadow-lg">
          <CardContent className="py-12">
            <div className="flex flex-col items-center justify-center space-y-8">
              
              <div className="relative">
                <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" style={{ animationDuration: "2.5s" }} />
                <div className="relative rounded-full bg-primary/10 p-6 shadow-sm border border-primary/20">
                  <Search className="h-12 w-12 text-primary animate-pulse" />
                </div>
              </div>

              <div className="w-full max-w-md space-y-4">
                <div className="flex justify-between items-end">
                  <h2 className="text-xl font-bold tracking-tight text-slate-800">
                    Sourcing Candidates...
                  </h2>
                  <span className="text-sm font-mono font-medium text-slate-500">
                    {progress}%
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                  <div 
                    className="h-full bg-primary transition-all duration-700 ease-out relative overflow-hidden" 
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite] w-full" style={{ backgroundImage: "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)" }}></div>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <p className="text-slate-600 font-medium truncate pr-4">
                    {message}
                  </p>
                  <span className="text-slate-400 font-mono text-xs whitespace-nowrap">
                    {status.elapsed_seconds ? `${status.elapsed_seconds}s` : '0s'}
                  </span>
                </div>
              </div>

              {isWakingBackend && (
                <div className="w-full max-w-md p-4 bg-blue-50 text-blue-800 rounded-lg border border-blue-200 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-500">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                    <div className="text-sm leading-snug">
                      <strong>Waking AI backend cluster...</strong><br />
                      This may take up to 30 seconds on first load.
                    </div>
                  </div>
                </div>
              )}
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
            <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4 text-left">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                <div>
                  <h3 className="font-semibold text-destructive text-sm">Pipeline Execution Failed</h3>
                  <p className="text-sm text-destructive/90 mt-1">{error}</p>
                  
                  {status?.status === "failed" && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-3 border-destructive/30 text-destructive hover:bg-destructive/10"
                      onClick={() => handleStartSourcing()}
                    >
                      Retry Pipeline
                    </Button>
                  )}
                </div>
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
            
            {isWakingBackend && isStarting && (
              <div className="mx-auto max-w-sm mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md text-left animate-in fade-in slide-in-from-bottom-2">
                <div className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                  <div className="text-sm text-blue-800">
                    <strong>Waking AI backend...</strong><br />
                    This may take up to 30 seconds on first load.
                  </div>
                </div>
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground">
            This will scan candidate profiles and rank them against your job description
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
