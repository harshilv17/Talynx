"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Edit, RefreshCw, Loader2 } from "lucide-react";

interface ActionPanelProps {
  onApprove: () => void;
  onEdit: () => void;
  onRevise: (feedback: string) => void;
  isSubmitting: boolean;
  isEditing: boolean;
  revisionNumber: number;
}

export function ActionPanel({
  onApprove,
  onEdit,
  onRevise,
  isSubmitting,
  isEditing,
  revisionNumber,
}: ActionPanelProps) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");

  const handleReviseClick = () => {
    if (showFeedback && feedback.trim()) {
      onRevise(feedback);
      setFeedback("");
      setShowFeedback(false);
    } else {
      setShowFeedback(true);
    }
  };

  const maxRevisionsReached = revisionNumber >= 3;

  return (
    <Card className="sticky top-20">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Actions</span>
          {revisionNumber > 0 && (
            <Badge variant="outline">
              Revision {revisionNumber}/3
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isEditing ? (
          <Button onClick={onEdit} size="lg" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Check className="mr-2 h-4 w-4" />
                Save & Publish
              </>
            )}
          </Button>
        ) : (
          <>
            <Button onClick={onApprove} size="lg" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Publishing...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Approve & Publish
                </>
              )}
            </Button>

            <Button
              onClick={onEdit}
              variant="secondary"
              size="lg"
              className="w-full"
              disabled={isSubmitting}
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit Inline
            </Button>

            <Button
              onClick={handleReviseClick}
              variant="ghost"
              size="lg"
              className="w-full"
              disabled={isSubmitting || maxRevisionsReached}
              title={maxRevisionsReached ? "Maximum revisions reached. Use inline edit instead." : ""}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Re-generate with Feedback
            </Button>

            {maxRevisionsReached && (
              <p className="text-xs text-muted-foreground text-center">
                Maximum revisions reached
              </p>
            )}
          </>
        )}

        {showFeedback && !isEditing && (
          <div className="pt-3 border-t space-y-2">
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Describe what you'd like to change..."
              rows={4}
            />
            <div className="flex gap-2">
              <Button
                onClick={handleReviseClick}
                disabled={!feedback.trim() || isSubmitting}
                size="sm"
                className="flex-1"
              >
                Submit Feedback
              </Button>
              <Button
                onClick={() => {
                  setShowFeedback(false);
                  setFeedback("");
                }}
                variant="ghost"
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
