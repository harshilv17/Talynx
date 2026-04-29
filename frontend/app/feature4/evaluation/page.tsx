"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, UserCheck, Star, FileText, CheckCircle, Search } from "lucide-react";
import { getApiBaseUrl } from "@/lib/utils";

interface EvaluationScores {
  technical_score: number;
  experience_score: number;
  overall_score: number;
}

interface DecisionResult {
  recommendation: string;
  confidence: number;
  reason: string;
}

interface Candidate {
  id: string;
  name: string;
  skills: string[];
  score: number;
  status: string;
  response?: string;
  evaluation?: EvaluationScores;
  decision?: DecisionResult;
}

function EvaluationContent() {
  const searchParams = useSearchParams();
  const jdId = searchParams.get("jdId");
  
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [evaluatingId, setEvaluatingId] = useState<string | null>(null);
  const [generatingOfferId, setGeneratingOfferId] = useState<string | null>(null);
  const [offerLetter, setOfferLetter] = useState<string | null>(null);
  const [offerDetails, setOfferDetails] = useState<{role: string, salary: string} | null>(null);
  const [offerCandidate, setOfferCandidate] = useState<Candidate | null>(null);
  const [sendingOfferId, setSendingOfferId] = useState<string | null>(null);

  useEffect(() => {
    if (!jdId) {
      setLoading(false);
      setError("No job ID provided.");
      return;
    }

    async function loadCandidates() {
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/v1/feature2/candidates?job_id=${jdId}`);
        if (!res.ok) throw new Error("Failed to load candidates");
        const data = await res.json();
        const responded = (data.candidates || []).filter(
          (c: Candidate) => c.status === "responded" || c.status === "evaluated" || c.status === "offered"
        );
        setCandidates(responded);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadCandidates();
  }, [jdId]);

  const handleEvaluate = async (candidate: Candidate) => {
    setEvaluatingId(candidate.id);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature4/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jdId,
          candidate_ids: [candidate.id]
        })
      });
      if (!res.ok) throw new Error("Evaluation failed");
      const data = await res.json();
      
      const evalResult = data.evaluated[0];
      if (evalResult) {
        setCandidates(prev => prev.map(c => 
          c.id === candidate.id ? { 
            ...c, 
            status: "evaluated", 
            evaluation: evalResult.evaluation,
            decision: evalResult.decision
          } : c
        ));
      }
    } catch (err) {
      console.error(err);
      alert("Failed to evaluate candidate.");
    } finally {
      setEvaluatingId(null);
    }
  };

  const handleGenerateOffer = async (candidate: Candidate) => {
    setGeneratingOfferId(candidate.id);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature4/generate-offer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidate.id,
          jd_id: jdId
        })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Offer generation failed");
      }
      const data = await res.json();
      
      setOfferLetter(data.offer_text);
      setOfferDetails({ role: data.role, salary: data.salary });
      setOfferCandidate(candidate);
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to generate offer.");
    } finally {
      setGeneratingOfferId(null);
    }
  };

  const handleConfirmOffer = async (candidate: Candidate) => {
    setSendingOfferId(candidate.id);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature4/offer/${candidate.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Offer sending failed");
      }
      
      setCandidates(prev => prev.map(c => 
        c.id === candidate.id ? { ...c, status: "offered" } : c
      ));
      setOfferLetter(null);
      setOfferCandidate(null);
      setOfferDetails(null);
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to send offer.");
    } finally {
      setSendingOfferId(null);
    }
  };

  const handleReject = async (candidate: Candidate) => {
    try {
      // Opting to quickly update UI for demo purposes
      setCandidates(prev => prev.map(c => 
        c.id === candidate.id ? { ...c, status: "rejected" } : c
      ));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 space-y-8">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-blue-100 p-6 mb-2">
            <UserCheck className="h-12 w-12 text-blue-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Feature 4 — Evaluation & Offer</h1>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto">
          Review candidates who responded to outreach, evaluate them, and generate automated offer letters.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between border-b pb-4">
          <h2 className="text-2xl font-semibold flex items-center gap-2 text-slate-800">
            <Search className="h-6 w-6 text-slate-500" />
            Responded Candidates
          </h2>
          <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">
            {candidates.length} Responses
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <Card className="border-destructive/20 bg-destructive/5">
            <CardContent className="py-8 text-center text-destructive">
              <p>{error}</p>
            </CardContent>
          </Card>
        ) : candidates.length === 0 ? (
          <Card className="border-dashed bg-slate-50">
            <CardContent className="py-16 text-center text-slate-500 space-y-4">
              <UserCheck className="h-12 w-12 mx-auto text-slate-300" />
              <p className="text-lg font-medium text-slate-700">No candidates responded yet.</p>
              <p>Wait for responses from the automated outreach sequence.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {candidates.map((candidate) => (
              <Card key={candidate.id} className="hover:shadow-md transition-shadow border-slate-200 flex flex-col">
                <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50">
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <CardTitle className="text-lg truncate">{candidate.name}</CardTitle>
                      <CardDescription className="text-xs mt-1">
                        Sourcing Match: <span className="font-semibold text-slate-700">{candidate.score}%</span>
                      </CardDescription>
                    </div>
                    {candidate.response && (
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full flex items-center gap-1 shrink-0 ${candidate.response === 'Interested' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {candidate.response}
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="pt-4 flex-1 space-y-4">
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.skills.slice(0, 5).map((skill, idx) => (
                      <span key={idx} className="bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded-md border border-slate-200">
                        {skill}
                      </span>
                    ))}
                  </div>

                  {candidate.evaluation ? (
                    <div className="bg-indigo-50/50 border border-indigo-100 rounded-md p-4 space-y-3">
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="h-4 w-4 text-indigo-500" />
                        <h4 className="font-semibold text-sm text-indigo-900">AI Evaluation Complete</h4>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-center text-xs">
                        <div className="bg-white p-2 rounded border border-indigo-100">
                          <div className="text-slate-500 mb-1">Technical</div>
                          <div className="font-bold text-indigo-700">{candidate.evaluation.technical_score}%</div>
                        </div>
                        <div className="bg-white p-2 rounded border border-indigo-100">
                          <div className="text-slate-500 mb-1">Experience</div>
                          <div className="font-bold text-indigo-700">{candidate.evaluation.experience_score}%</div>
                        </div>
                        <div className="bg-white p-2 rounded border border-indigo-100">
                          <div className="text-slate-500 mb-1">Overall</div>
                          <div className="font-bold text-indigo-700">{candidate.evaluation.overall_score}%</div>
                        </div>
                      </div>
                      {candidate.decision && (
                        <div className={`mt-3 text-sm font-semibold text-center p-2 rounded border ${candidate.decision.recommendation.startsWith('hire') ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200'}`}>
                          Decision: {candidate.decision.recommendation === 'hire_high' ? 'HIRE (Strong)' : candidate.decision.recommendation === 'hire_moderate' ? 'HIRE (Moderate)' : 'NO HIRE'}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500 italic py-2">
                      Ready for deep evaluation.
                    </div>
                  )}

                  <div className="pt-2">
                    {!candidate.evaluation && candidate.status === "responded" && (
                       <Button 
                        className="w-full" 
                        onClick={() => handleEvaluate(candidate)}
                        disabled={evaluatingId === candidate.id}
                      >
                        {evaluatingId === candidate.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <FileText className="h-4 w-4 mr-2" />}
                        Evaluate Candidate
                      </Button>
                    )}
                    
                    {candidate.evaluation && (candidate.status === "responded" || candidate.status === "evaluated") && (
                       <div className="flex gap-2">
                         <Button 
                          className="w-full bg-slate-100 text-slate-700 hover:bg-slate-200" 
                          onClick={() => handleReject(candidate)}
                        >
                          Reject
                        </Button>
                         <Button 
                          className="w-full bg-green-600 hover:bg-green-700" 
                          onClick={() => handleGenerateOffer(candidate)}
                          disabled={generatingOfferId === candidate.id}
                        >
                          {generatingOfferId === candidate.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <CheckCircle className="h-4 w-4 mr-2" />}
                          Generate Offer Letter
                        </Button>
                       </div>
                    )}
                    
                    {candidate.status === "offered" && (
                      <Button className="w-full bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200" disabled>
                        Offer Generated
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {offerLetter && offerCandidate && offerDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-2xl shadow-2xl max-h-[90vh] flex flex-col">
            <CardHeader className="border-b bg-slate-50 flex flex-row items-center justify-between">
              <div>
                <CardTitle>Offer Letter: {offerCandidate.name}</CardTitle>
                <CardDescription>
                  <span className="font-medium text-slate-700">Role:</span> {offerDetails.role} &nbsp;|&nbsp; 
                  <span className="font-medium text-slate-700">Salary:</span> {offerDetails.salary}
                </CardDescription>
              </div>
              <Button variant="ghost" onClick={() => setOfferLetter(null)}>Cancel</Button>
            </CardHeader>
            <CardContent className="p-6 overflow-y-auto">
              <pre className="whitespace-pre-wrap font-serif text-slate-800 text-sm leading-relaxed border p-4 rounded-md bg-white">
                {offerLetter}
              </pre>
            </CardContent>
            <div className="p-4 border-t bg-slate-50 flex justify-end gap-2">
               <Button variant="outline" onClick={() => setOfferLetter(null)}>Cancel</Button>
               <Button 
                variant="outline" 
                onClick={() => {
                  const blob = new Blob([offerLetter!], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `Offer_Letter_${offerCandidate.name.replace(/\s+/g, '_')}.txt`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
               >
                 Download Offer
               </Button>
               <Button 
                className="bg-green-600 hover:bg-green-700"
                onClick={() => handleConfirmOffer(offerCandidate)}
                disabled={sendingOfferId === offerCandidate.id}
               >
                 {sendingOfferId === offerCandidate.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                 Confirm & Send
               </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

export default function EvaluationPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}>
      <EvaluationContent />
    </Suspense>
  );
}
