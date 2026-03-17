"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface JDContent {
  job_title: string;
  tagline: string;
  about_role: string;
  responsibilities: string[];
  requirements: string[];
  nice_to_haves: string[];
  company_blurb: string;
  salary_range: string;
  location_work_type: string;
}

interface JDPreviewProps {
  jd: JDContent;
  isEditing: boolean;
  editedJd: JDContent;
  onJdChange: (jd: JDContent) => void;
}

export function JDPreview({ jd, isEditing, editedJd, onJdChange }: JDPreviewProps) {
  const displayJd = isEditing ? editedJd : jd;

  const handleFieldChange = (field: keyof JDContent, value: any) => {
    onJdChange({ ...editedJd, [field]: value });
  };

  const handleListItemChange = (
    field: "responsibilities" | "requirements" | "nice_to_haves",
    index: number,
    value: string
  ) => {
    const newList = [...editedJd[field]];
    newList[index] = value;
    handleFieldChange(field, newList);
  };

  return (
    <Card className="shadow-lg">
      <CardHeader className="space-y-4 pb-4">
        {isEditing ? (
          <>
            <Input
              value={editedJd.job_title}
              onChange={(e) => handleFieldChange("job_title", e.target.value)}
              className="text-3xl font-bold h-auto py-2"
            />
            <Input
              value={editedJd.tagline}
              onChange={(e) => handleFieldChange("tagline", e.target.value)}
              className="text-lg text-slate-600"
            />
          </>
        ) : (
          <>
            <h1 className="text-3xl font-bold">{displayJd.job_title}</h1>
            <p className="text-lg text-slate-600">{displayJd.tagline}</p>
          </>
        )}

        <div className="flex gap-4 text-sm text-slate-600">
          {isEditing ? (
            <Input
              value={editedJd.location_work_type}
              onChange={(e) => handleFieldChange("location_work_type", e.target.value)}
              className="flex-1"
            />
          ) : (
            <span>{displayJd.location_work_type}</span>
          )}
          <span className="font-semibold text-slate-900">
            {isEditing ? (
              <Input
                value={editedJd.salary_range}
                onChange={(e) => handleFieldChange("salary_range", e.target.value)}
                className="w-48"
              />
            ) : (
              displayJd.salary_range
            )}
          </span>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <section>
          <h2 className="text-xl font-semibold mb-3">About the Role</h2>
          {isEditing ? (
            <Textarea
              value={editedJd.about_role}
              onChange={(e) => handleFieldChange("about_role", e.target.value)}
              rows={3}
            />
          ) : (
            <p className="text-slate-700 leading-relaxed">{displayJd.about_role}</p>
          )}
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Responsibilities</h2>
          <ul className="space-y-2">
            {displayJd.responsibilities.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                {isEditing ? (
                  <Input
                    value={editedJd.responsibilities[idx]}
                    onChange={(e) =>
                      handleListItemChange("responsibilities", idx, e.target.value)
                    }
                    className="flex-1"
                  />
                ) : (
                  <span className="text-slate-700">{item}</span>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Requirements</h2>
          <ul className="space-y-2">
            {displayJd.requirements.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                {isEditing ? (
                  <Input
                    value={editedJd.requirements[idx]}
                    onChange={(e) => handleListItemChange("requirements", idx, e.target.value)}
                    className="flex-1"
                  />
                ) : (
                  <span className="text-slate-700">{item}</span>
                )}
              </li>
            ))}
          </ul>
        </section>

        {displayJd.nice_to_haves.length > 0 && (
          <section>
            <h2 className="text-xl font-semibold mb-3">Nice to Have</h2>
            <ul className="space-y-2">
              {displayJd.nice_to_haves.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  {isEditing ? (
                    <Input
                      value={editedJd.nice_to_haves[idx]}
                      onChange={(e) => handleListItemChange("nice_to_haves", idx, e.target.value)}
                      className="flex-1"
                    />
                  ) : (
                    <span className="text-slate-700">{item}</span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        <section>
          <h2 className="text-xl font-semibold mb-3">About the Company</h2>
          {isEditing ? (
            <Textarea
              value={editedJd.company_blurb}
              onChange={(e) => handleFieldChange("company_blurb", e.target.value)}
              rows={3}
            />
          ) : (
            <p className="text-slate-700 leading-relaxed">{displayJd.company_blurb}</p>
          )}
        </section>
      </CardContent>
    </Card>
  );
}
