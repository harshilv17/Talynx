import React, { useState } from "react";
import { Mail, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { EvaluationCandidate, generateOffer } from "../../services/feature4";
import { OfferModal } from "./OfferModal";

export function DecisionSection({ candidate }: { candidate: EvaluationCandidate }) {
  const { decision } = candidate;
  const isHire = decision.recommendation === "hire";

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offerText, setOfferText] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleGenerateOffer = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);
    setError(null);

    try {
      const text = await generateOffer(candidate.id);
      setOfferText(text);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.message);
      setTimeout(() => setError(null), 5000); 
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-sm text-gray-500 uppercase tracking-wider">Decision Details</h4>
      
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-500">Confidence</span>
          <span className="text-sm font-medium">{(decision.confidence * 100).toFixed(0)}%</span>
        </div>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          {decision.reason}
        </p>
      </div>

      {isHire && (
        <div className="pt-4 flex flex-col items-end gap-2">
          <button
            onClick={handleGenerateOffer}
            disabled={loading}
            className="flex items-center justify-center min-w-[140px] gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors text-sm shadow-sm"
          >
            {loading ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Generating...</>
            ) : offerText ? (
              <><CheckCircle2 className="h-4 w-4" /> View Offer</>
            ) : (
              <><Mail className="h-4 w-4" /> Generate Offer</>
            )}
          </button>
          
          {error && (
            <span className="flex items-center gap-1 text-xs text-red-600">
              <AlertCircle className="h-3 w-3" /> {error}
            </span>
          )}
        </div>
      )}

      <OfferModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        candidateName={candidate.name}
        offerText={offerText || ""}
      />
    </div>
  );
}
