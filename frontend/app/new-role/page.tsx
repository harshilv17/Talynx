import { RoleBriefForm } from "@/components/intake/RoleBriefForm";

export default function NewRolePage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Create New Role</h1>
        <p className="text-slate-600">
          Fill out the form below to generate an AI-powered job description
        </p>
      </div>

      <RoleBriefForm />
    </div>
  );
}
