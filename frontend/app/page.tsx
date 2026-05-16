"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getApiBaseUrl } from "@/lib/utils";
import { Briefcase, Users, Mail, FileText, Loader2, Plus, ChevronRight, CheckCircle, Clock } from "lucide-react";
import { PipelineActionMenu } from "@/components/PipelineActionMenu";
import { completePipeline, archivePipeline, restorePipeline, deletePipeline } from "@/services/dashboard";

interface JobStats {
  total: number;
  shortlisted: number;
  rejected: number;
  saved: number;
  pending: number;
  hired: number;
}

interface JobData {
  job_id: string;
  title: string;
  pipeline_status: string;
  duration_days: number;
  created_at?: string;
  stats: JobStats;
  hired_candidates?: string[];
}

export default function Home() {
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"ACTIVE" | "COMPLETED" | "ARCHIVED">("ACTIVE");

  async function loadDashboard() {
    setLoading(true);
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

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleAction = async (action: (id: string) => Promise<any>, jobId: string) => {
    try {
      await action(jobId);
      await loadDashboard();
    } catch (e) {
      alert("Action failed. Please try again.");
    }
  };

  const filteredJobs = jobs.filter(j => j.pipeline_status === activeTab);

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-12 px-4 sm:px-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Pipeline Dashboard</h1>
          <p className="text-lg text-slate-500">Manage your recruitment lifecycles.</p>
        </div>
        <Link href="/new-role">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            Create New Role
          </Button>
        </Link>
      </div>

      <div className="flex border-b border-slate-200">
        {(["ACTIVE", "COMPLETED", "ARCHIVED"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab 
                ? "border-primary text-primary" 
                : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
            }`}
          >
            {tab.charAt(0) + tab.slice(1).toLowerCase()} ({jobs.filter(j => j.pipeline_status === tab).length})
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filteredJobs.length === 0 ? (
        <Card className="border-dashed shadow-none bg-slate-50/50">
          <CardContent className="py-16 text-center text-slate-500">
            <Briefcase className="h-12 w-12 mx-auto text-slate-300 mb-4" />
            <p className="text-lg font-medium text-slate-900 mb-1">No {activeTab.toLowerCase()} pipelines found</p>
            <p className="mb-4">
              {activeTab === "ACTIVE" && "Get started by creating your first job description."}
              {activeTab === "COMPLETED" && "Mark an active pipeline as 'Complete Hiring' when done."}
              {activeTab === "ARCHIVED" && "Archived pipelines will appear here."}
            </p>
            {activeTab === "ACTIVE" && (
              <Link href="/new-role">
                <Button variant="outline">Create New Role</Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {filteredJobs.map(job => {
            const isCompleted = job.pipeline_status === "COMPLETED";
            return (
              <Card key={job.job_id} className={`overflow-visible hover:border-slate-300 transition-colors relative group ${isCompleted ? "opacity-80" : ""}`}>
                <div className="flex flex-col md:flex-row">
                  {/* Info Section */}
                  <div className="p-6 md:w-1/3 border-b md:border-b-0 md:border-r bg-slate-50/50 flex flex-col justify-center relative">
                    <div className="absolute top-4 right-4 z-20">
                      <PipelineActionMenu 
                        jobId={job.job_id}
                        status={job.pipeline_status}
                        onComplete={() => handleAction(completePipeline, job.job_id)}
                        onArchive={() => handleAction(archivePipeline, job.job_id)}
                        onRestore={() => handleAction(restorePipeline, job.job_id)}
                        onDelete={() => handleAction(deletePipeline, job.job_id)}
                      />
                    </div>
                    <div className="flex items-center gap-2 mb-2 pr-8">
                      <Badge variant="outline" className={`uppercase tracking-wider ${
                        job.pipeline_status === 'ACTIVE' ? 'bg-green-100 text-green-800 border-green-200' : 
                        job.pipeline_status === 'COMPLETED' ? 'bg-blue-100 text-blue-800 border-blue-200' :
                        'bg-amber-100 text-amber-800 border-amber-200'
                      }`}>
                        {job.pipeline_status}
                      </Badge>
                      <span className="text-xs text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {job.duration_days} days
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2 truncate" title={job.title}>
                      <Link href={`/sourcing/${job.job_id}`} className="hover:underline after:absolute after:inset-0">
                        {job.title}
                      </Link>
                    </h3>
                    <p className="text-sm text-slate-500 truncate" title={job.job_id}>ID: {job.job_id.slice(0, 8)}...</p>
                  </div>
                  
                  {/* Stats Section */}
                  <div className="p-6 md:w-2/3 grid grid-cols-2 sm:grid-cols-4 gap-4 pointer-events-none">
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Total Sourced</p>
                      <p className="text-2xl font-bold text-slate-900">{job.stats.total}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Shortlisted</p>
                      <p className="text-2xl font-bold text-slate-900">{job.stats.shortlisted}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Rejected</p>
                      <p className="text-2xl font-bold text-slate-900">{job.stats.rejected}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-500">Hired</p>
                      <p className="text-2xl font-bold text-green-600">{job.stats.hired}</p>
                    </div>
                  </div>
                </div>
                
                {isCompleted && job.hired_candidates && job.hired_candidates.length > 0 && (
                  <div className="w-full bg-green-50/80 p-3 border-t border-green-100 flex items-center justify-between text-sm text-green-800">
                     <span className="font-medium flex items-center gap-2">
                       <CheckCircle className="h-4 w-4" /> 
                       Successfully Hired: {job.hired_candidates.join(", ")}
                     </span>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
