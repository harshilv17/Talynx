"use client";

import Link from "next/link";
import { CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface SuccessScreenProps {
  threadId: string;
}

export function SuccessScreen({ threadId }: SuccessScreenProps) {
  return (
    <div className="max-w-2xl mx-auto py-12">
      <Card className="shadow-lg">
        <CardContent className="pt-6 space-y-6 text-center">
          <div className="flex justify-center">
            <div className="rounded-full bg-green-100 p-6">
              <CheckCircle className="h-16 w-16 text-green-600" />
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Job Description Published!</h1>
            <p className="text-slate-600">
              Your job description has been successfully published and is ready for the next stage.
            </p>
          </div>

          <div className="pt-4">
            <Link href={`/sourcing/${threadId}`}>
              <Button size="lg" id="start-sourcing-link">
                Start sourcing candidates
              </Button>
            </Link>
          </div>

          <div className="text-xs text-muted-foreground">
            Feature 2: Sourcing &amp; Screening will find and rank the best candidates
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
