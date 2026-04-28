"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
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
  const searchParams = useSearchParams();
  const jdId = searchParams.get("jdId");
  
  const [candidates, setCandidates] = useState<ShortlistedCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
                  <Button className="w-full mt-6" variant="outline">
                    Preview Outreach Email
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {candidates.length > 0 && (
        <div className="flex justify-end pt-4">
          <Button size="lg" className="px-8">
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
