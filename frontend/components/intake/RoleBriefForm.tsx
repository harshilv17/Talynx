"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SkillTagInput } from "./SkillTagInput";
import { getApiBaseUrl } from "@/lib/utils";
import { SalaryBandInput } from "./SalaryBandInput";
import { ToneSelector } from "./ToneSelector";
import { Loader2, X } from "lucide-react";

export function RoleBriefForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    role_title: "",
    team: "",
    seniority: "mid",
    work_type: "hybrid",
    location: "",
    must_have_skills: [] as string[],
    nice_to_have_skills: [] as string[],
    salary_min: 0,
    salary_max: 0,
    currency: "USD",
    headcount: 1,
    years_of_experience: undefined as number | undefined,
    reports_to: "",
    key_outcomes: [] as string[],
    context_note: "",
    tone_preference: "conversational",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.must_have_skills.length === 0) {
      setError("Please add at least one must-have skill.");
      return;
    }
    if (!formData.salary_min || !formData.salary_max) {
      setError("Please fill in both salary minimum and maximum.");
      return;
    }
    if (formData.salary_max < formData.salary_min) {
      setError("Salary maximum must be greater than or equal to minimum.");
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        ...formData,
        years_of_experience: formData.years_of_experience || null,
        reports_to: formData.reports_to || null,
        key_outcomes: formData.key_outcomes.length > 0 ? formData.key_outcomes : null,
        context_note: formData.context_note || null,
      };

      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/feature1/start`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let message = "Failed to start job generation";
        if (typeof errorData.detail === "string") {
          message = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          message = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
        }
        throw new Error(message);
      }

      const data = await response.json();
      router.push(`/review/${data.thread_id}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setIsSubmitting(false);
    }
  };

  const [keyOutcomeInput, setKeyOutcomeInput] = useState("");

  const handleKeyOutcomeKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && keyOutcomeInput.trim()) {
      e.preventDefault();
      if (!formData.key_outcomes.includes(keyOutcomeInput.trim())) {
        setFormData({
          ...formData,
          key_outcomes: [...formData.key_outcomes, keyOutcomeInput.trim()],
        });
      }
      setKeyOutcomeInput("");
    }
  };

  const removeKeyOutcome = (outcome: string) => {
    setFormData({
      ...formData,
      key_outcomes: formData.key_outcomes.filter((o) => o !== outcome),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Role Basics</CardTitle>
          <CardDescription>Tell us about the position you need to fill</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="role_title">Role Title *</Label>
            <Input
              id="role_title"
              required
              value={formData.role_title}
              onChange={(e) => setFormData({ ...formData, role_title: e.target.value })}
              placeholder="e.g. Senior Software Engineer"
            />
          </div>

          <div>
            <Label htmlFor="team">Team *</Label>
            <Input
              id="team"
              required
              value={formData.team}
              onChange={(e) => setFormData({ ...formData, team: e.target.value })}
              placeholder="e.g. Engineering, Product, Data"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="seniority">Seniority Level *</Label>
              <Select
                value={formData.seniority}
                onValueChange={(value) => setFormData({ ...formData, seniority: value })}
              >
                <SelectTrigger id="seniority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="entry">Entry</SelectItem>
                  <SelectItem value="junior">Junior</SelectItem>
                  <SelectItem value="mid">Mid-Level</SelectItem>
                  <SelectItem value="senior">Senior</SelectItem>
                  <SelectItem value="staff">Staff</SelectItem>
                  <SelectItem value="principal">Principal</SelectItem>
                  <SelectItem value="lead">Lead</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="headcount">Number of Hires *</Label>
              <Input
                id="headcount"
                type="number"
                min="1"
                required
                value={formData.headcount}
                onChange={(e) => setFormData({ ...formData, headcount: Number(e.target.value) })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Location & Work Type</CardTitle>
          <CardDescription>Where will this person work?</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="work_type">Work Type *</Label>
              <Select
                value={formData.work_type}
                onValueChange={(value) => setFormData({ ...formData, work_type: value })}
              >
                <SelectTrigger id="work_type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="remote">Remote</SelectItem>
                  <SelectItem value="hybrid">Hybrid</SelectItem>
                  <SelectItem value="onsite">Onsite</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                required
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="e.g. San Francisco, CA or Remote (US)"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Skills & Requirements</CardTitle>
          <CardDescription>What skills and experience are you looking for?</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Must-Have Skills *</Label>
            <SkillTagInput
              label="Must-have skills"
              skills={formData.must_have_skills}
              onSkillsChange={(skills) => setFormData({ ...formData, must_have_skills: skills })}
              placeholder="Type a skill and press Enter"
            />
            <p className="text-xs text-muted-foreground mt-1">
              At least one must-have skill is required
            </p>
          </div>

          <div>
            <Label>Nice-to-Have Skills</Label>
            <SkillTagInput
              label="Nice-to-have skills"
              skills={formData.nice_to_have_skills}
              onSkillsChange={(skills) => setFormData({ ...formData, nice_to_have_skills: skills })}
            />
          </div>

          <div>
            <Label htmlFor="years_of_experience">Years of Experience</Label>
            <Input
              id="years_of_experience"
              type="number"
              min="0"
              value={formData.years_of_experience || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  years_of_experience: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              placeholder="e.g. 3"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Compensation</CardTitle>
          <CardDescription>Define the salary range for this role</CardDescription>
        </CardHeader>
        <CardContent>
          <SalaryBandInput
            minValue={formData.salary_min}
            maxValue={formData.salary_max}
            currency={formData.currency}
            onMinChange={(value) => setFormData({ ...formData, salary_min: value })}
            onMaxChange={(value) => setFormData({ ...formData, salary_max: value })}
            onCurrencyChange={(value) => setFormData({ ...formData, currency: value })}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Additional Context</CardTitle>
          <CardDescription>Optional details to help the AI generate a better JD</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="reports_to">Reports To</Label>
            <Input
              id="reports_to"
              value={formData.reports_to}
              onChange={(e) => setFormData({ ...formData, reports_to: e.target.value })}
              placeholder="e.g. VP of Engineering"
            />
          </div>

          <div>
            <Label>Key Outcomes</Label>
            <Input
              value={keyOutcomeInput}
              onChange={(e) => setKeyOutcomeInput(e.target.value)}
              onKeyDown={handleKeyOutcomeKeyDown}
              placeholder="Type a key outcome and press Enter"
            />
            {formData.key_outcomes.length > 0 && (
              <div className="mt-2 space-y-2">
                {formData.key_outcomes.map((outcome, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-secondary p-2 rounded-md"
                  >
                    <span className="text-sm">{outcome}</span>
                    <button
                      type="button"
                      onClick={() => removeKeyOutcome(outcome)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <Label htmlFor="context_note">Context Note</Label>
            <Textarea
              id="context_note"
              value={formData.context_note}
              onChange={(e) => setFormData({ ...formData, context_note: e.target.value })}
              placeholder="Any additional context about the role, team, or what you're looking for..."
              rows={4}
            />
          </div>

          <div>
            <Label htmlFor="tone_preference">Tone Preference</Label>
            <ToneSelector
              value={formData.tone_preference}
              onChange={(value) => setFormData({ ...formData, tone_preference: value })}
            />
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      <div className="flex justify-end">
        <Button type="submit" size="lg" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Starting generation...
            </>
          ) : (
            "Generate job description with AI"
          )}
        </Button>
      </div>
    </form>
  );
}
