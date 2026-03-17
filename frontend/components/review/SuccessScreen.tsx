"use client";

import { CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export function SuccessScreen() {
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
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="inline-block">
                    <Button size="lg" disabled>
                      Start sourcing candidates
                    </Button>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Coming soon in Feature 2</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <div className="text-xs text-muted-foreground">
            Feature 2: Sourcing & Screening is coming soon
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
