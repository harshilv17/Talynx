import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-12">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">
          Welcome to ATA
        </h1>
        <p className="text-xl text-slate-600">
          AI-powered hiring automation from intake to offer
        </p>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle>Feature 1: Intake & JD Generation</CardTitle>
          <CardDescription>
            Create AI-generated job descriptions with built-in compliance checks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-700">
            Submit a role brief and receive a professionally written, bias-free job description 
            that you can review, edit, and publish.
          </p>
          <Link href="/new-role">
            <Button size="lg" className="w-full sm:w-auto">
              Create New Role
            </Button>
          </Link>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Feature 2</CardTitle>
            <CardDescription>Sourcing & Screening</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">Coming soon</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Feature 3</CardTitle>
            <CardDescription>Outreach & Interviews</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">Coming soon</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Feature 4</CardTitle>
            <CardDescription>Evaluation & Offer</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600">Coming soon</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
