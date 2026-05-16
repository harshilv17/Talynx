"use client";

import { useState, useRef, useEffect } from "react";
import { MoreVertical, CheckCircle, Archive, RotateCcw, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PipelineActionMenuProps {
  jobId: string;
  status: string;
  onComplete: () => void;
  onArchive: () => void;
  onRestore: () => void;
  onDelete: () => void;
}

export function PipelineActionMenu({
  jobId,
  status,
  onComplete,
  onArchive,
  onRestore,
  onDelete,
}: PipelineActionMenuProps) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleAction = (action: () => void, confirmMessage?: string) => {
    setOpen(false);
    if (confirmMessage) {
      if (window.confirm(confirmMessage)) {
        action();
      }
    } else {
      action();
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <Button
        variant="ghost"
        size="sm"
        className="h-8 w-8 p-0 text-slate-500 hover:text-slate-900 focus:ring-0 z-20 relative"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(!open);
        }}
      >
        <MoreVertical className="h-4 w-4" />
      </Button>

      {open && (
        <div 
          className="absolute right-0 top-full mt-1 w-48 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 z-50 py-1"
          onClick={(e) => e.stopPropagation()} // prevent clicking menu from navigating
        >
          {status !== "COMPLETED" && status !== "ARCHIVED" && (
            <button
              onClick={(e) => { e.preventDefault(); handleAction(onComplete, "Are you sure you want to Complete this hiring pipeline? This will disable sourcing and offers."); }}
              className="flex w-full items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
              Complete Hiring
            </button>
          )}

          {status !== "ARCHIVED" && (
            <button
              onClick={(e) => { e.preventDefault(); handleAction(onArchive, "Are you sure you want to Archive this pipeline? It will be hidden from the active dashboard."); }}
              className="flex w-full items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              <Archive className="mr-2 h-4 w-4 text-amber-600" />
              Archive Pipeline
            </button>
          )}

          {(status === "COMPLETED" || status === "ARCHIVED") && (
            <button
              onClick={(e) => { e.preventDefault(); handleAction(onRestore); }}
              className="flex w-full items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              <RotateCcw className="mr-2 h-4 w-4 text-blue-600" />
              Restore Pipeline
            </button>
          )}

          <div className="my-1 border-t border-slate-100"></div>

          <button
            onClick={(e) => { e.preventDefault(); handleAction(onDelete, "Are you sure you want to Delete this pipeline? This cannot be undone."); }}
            className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete Pipeline
          </button>
        </div>
      )}
    </div>
  );
}
