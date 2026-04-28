"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getApiBaseUrl } from "@/lib/utils";
import { Briefcase, Users, Mail, FileText, Loader2, Plus, ChevronRight } from "lucide-react";

interface JobStats {
  total: number;
  shortlisted: number;
  rejected: number;
  saved: number;
  pending: number;
}

interface JobData {
  job_id: string;
  title: string;
  status: string;
  stats: JobStats;
  outreach: { emails_sent: number; responses: number };
  offers: { generated: number; accepted: number };
}

export default function Home() {
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/v1/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setJobs(data.jobs);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-12 px-4 sm:px-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Welcome to ATA</h1>
          <p className="text-lg text-slate-500">Your AI-powered ATS dashboard.</p>
        </div>
        <Link href="/new-role">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            Create New Role
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : jobs.length === 0 ? (
        <Card className="border-dashed shadow-none">
          <CardContent className="py-12 text-center text-slate-500">
            <Briefcase className="h-12 w-12 mx-auto text-slate-300 mb-4" />
            <p className="text-lg font-medium text-slate-900 mb-1">No roles found</p>
            <p className="mb-4">Get started by creating your first job description.</p>
            <Link href="/new-role">
              <Button variant="outline">Create New Role</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <h2 className="text-xl font-semibold text-slate-900 border-b pb-2">Active Pipelines</h2>
          {jobs.map(job => {
            const isPublished = job.status === "published";
            const routeUrl = isPublished ? `/sourcing/${job.job_id}` : `/review/${job.job_id}`;
            return (
              <Card key={job.job_id} className="overflow-hidden hover:border-slate-300 transition-colors relative group">
                <Link href={routeUrl} className="absolute inset-0 z-10" aria-label={`View pipeline for ${job.title}`} />
                <div className="flex flex-col md:flex-row">
                  {/* Info Section */}
                  <div className="p-6 md:w-1/3 border-b md:border-b-0 md:border-r bg-slate-50/50 flex flex-col justify-center">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full uppercase tracking-wider
                        ${isPublished ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                      `}>
                        {job.status}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2 truncate" title={job.title}>
                      {job.title}
                    </h3>
                    <p className="text-sm text-slate-500 truncate" title={job.job_id}>ID: {job.job_id.slice(0, 8)}...</p>
                  </div>
                  
                  {/* Stats Section */}
                  <div className="p-6 md:w-2/3 grid grid-cols-3 gap-4">
                    {/* Candidates */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                        <Users className="h-4 w-4" /> Sourcing
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{job.stats.total}</div>
                      <div className="text-xs text-slate-500">
                        {job.stats.shortlisted} shortlisted • {job.stats.pending} pending
                      </div>
                    </div>

                    {/* Outreach */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                        <Mail className="h-4 w-4" /> Outreach
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{job.outreach.emails_sent}</div>
                      <div className="text-xs text-slate-500">
                        {job.outreach.responses} responded
                      </div>
                    </div>

                    {/* Offers */}
                    <div className="space-y-2 relative">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                        <FileText className="h-4 w-4" /> Offers
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{job.offers.generated}</div>
                      <div className="text-xs text-slate-500">
                        {job.offers.accepted} accepted
                      </div>
                      
                      <div className="absolute top-1/2 -translate-y-1/2 -right-2 p-2 text-slate-300 group-hover:text-slate-900 transition-colors z-20">
                        <ChevronRight className="h-6 w-6" />
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
