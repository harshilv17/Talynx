"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Mail, Users, CheckCircle } from "lucide-react";
import { getApiBaseUrl } from "@/lib/utils";

interface ShortlistedCandidate {
  id: string;
  name: string;
  skills: string[];
  score: number;
  status: string;
}

function OutreachContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jdId = searchParams.get("jdId");
  
  const [candidates, setCandidates] = useState<ShortlistedCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Preview State
  const [previewData, setPreviewData] = useState<{subject: string, body: string} | null>(null);
  const [previewCandidate, setPreviewCandidate] = useState<ShortlistedCandidate | null>(null);
  const [isPreviewing, setIsPreviewing] = useState<string | null>(null); // holds candidate id
  const [isStarting, setIsStarting] = useState(false);
  const [outreachSuccess, setOutreachSuccess] = useState(false);

  useEffect(() => {
    if (!jdId) {
      setLoading(false);
      setError("No job ID provided.");
      return;
    }

    async function loadShortlisted() {
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/v1/feature2/shortlisted?jd_id=${jdId}`);
        if (!res.ok) throw new Error("Failed to load candidates");
        const data = await res.json();
        setCandidates(data.candidates || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadShortlisted();
  }, [jdId]);

  const handlePreviewEmail = async (candidate: ShortlistedCandidate) => {
    setIsPreviewing(candidate.id);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature3/preview-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate,
          job_description: {} // Simplified for the demo
        })
      });
      if (!res.ok) throw new Error("Failed to preview email");
      const data = await res.json();
      setPreviewData(data);
      setPreviewCandidate(candidate);
    } catch (err) {
      console.error(err);
      alert("Failed to preview email");
    } finally {
      setIsPreviewing(null);
    }
  };

  const handleStartOutreach = async () => {
    setIsStarting(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/feature3/start-outreach`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd_id: jdId })
      });
      if (!res.ok) throw new Error("Failed to start outreach");
      setOutreachSuccess(true);
    } catch (err) {
      console.error(err);
      alert("Failed to start outreach sequence");
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-12 px-4 space-y-8">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-indigo-100 p-6 mb-2">
            <Mail className="h-12 w-12 text-indigo-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Feature 3 — Outreach</h1>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto">
          Review your shortlisted candidates and prepare to initiate automated, personalized email outreach pipelines.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between border-b pb-4">
          <h2 className="text-2xl font-semibold flex items-center gap-2 text-slate-800">
            <Users className="h-6 w-6 text-slate-500" />
            Shortlisted Candidates
          </h2>
          <span className="bg-indigo-100 text-indigo-800 text-sm font-semibold px-3 py-1 rounded-full">
            {candidates.length} Ready for Outreach
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
              <Users className="h-12 w-12 mx-auto text-slate-300" />
              <p className="text-lg font-medium text-slate-700">No candidates found.</p>
              <p>You haven't shortlisted any candidates for this job yet.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {candidates.map((candidate) => (
              <Card key={candidate.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start gap-4">
                    <CardTitle className="text-lg truncate" title={candidate.name}>
                      {candidate.name}
                    </CardTitle>
                    <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded-full flex items-center gap-1 shrink-0">
                      <CheckCircle className="h-3 w-3" />
                      {candidate.score}%
                    </span>
                  </div>
                  <CardDescription className="flex items-center gap-1 text-xs">
                    <span className="uppercase tracking-wider font-semibold text-slate-500">{candidate.status}</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {candidate.skills.slice(0, 5).map((skill, idx) => (
                      <span key={idx} className="bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded-md border border-slate-200">
                        {skill}
                      </span>
                    ))}
                    {candidate.skills.length > 5 && (
                      <span className="text-xs text-slate-400 py-1">+{candidate.skills.length - 5} more</span>
                    )}
                  </div>
                  <Button 
                    className="w-full mt-6" 
                    variant="outline"
                    onClick={() => handlePreviewEmail(candidate)}
                    disabled={isPreviewing === candidate.id}
                  >
                    {isPreviewing === candidate.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Preview Outreach Email
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {previewData && previewCandidate && (
        <Card className="border-indigo-200 bg-indigo-50 mt-8 shadow-sm">
          <CardHeader className="border-b border-indigo-100 pb-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg text-indigo-900">Email Preview: {previewCandidate.name}</CardTitle>
              <CardDescription className="text-indigo-700 mt-1 font-medium">Subject: {previewData.subject}</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setPreviewData(null)} className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-100">Close</Button>
          </CardHeader>
          <CardContent className="pt-4">
            <pre className="whitespace-pre-wrap font-sans text-slate-700 text-sm leading-relaxed">
              {previewData.body}
            </pre>
          </CardContent>
        </Card>
      )}

      {outreachSuccess && (
        <div className="bg-green-100 text-green-800 p-4 rounded-md text-center font-medium border border-green-200">
          Success! The automated outreach sequence has been initiated for all shortlisted candidates.
        </div>
      )}

      {outreachSuccess && (
        <div className="flex justify-end pt-4">
          <Button size="lg" className="px-8" onClick={() => router.push(`/feature4/evaluation?jdId=${jdId}`)}>
            Proceed to Evaluation &rarr;
          </Button>
        </div>
      )}

      {candidates.length > 0 && !outreachSuccess && (
        <div className="flex justify-end pt-4">
          <Button size="lg" className="px-8" onClick={handleStartOutreach} disabled={isStarting}>
            {isStarting ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : null}
            Start Email Outreach Sequence &rarr;
          </Button>
        </div>
      )}
    </div>
  );
}

export default function OutreachPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}>
      <OutreachContent />
    </Suspense>
  );
}
