"use client";

import { useRouter } from "next/navigation";
import QuestionCard from "@/components/session/QuestionCard";
import { getQuestionSet } from "@/lib/questions";

export default function AssessmentPage() {
  const router = useRouter();
  const question = getQuestionSet("diagnostic")[0];

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex items-center gap-3 px-5 pt-4.5 pb-2">
        <button
          onClick={() => router.push("/onboarding")}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line bg-paper-raised text-ink-soft"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3 w-3">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
        <div className="flex-1">
          <div className="mb-1.5 flex justify-between font-mono text-[11px] text-ink-soft">
            <span>Question 1 of 3 · Diagnostic</span>
            <span>Reading</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-line">
            <div className="h-full w-[12%] rounded-full bg-primary transition-all duration-500" />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-1">
        <QuestionCard
          question={question}
          continueLabel="See my results"
          onContinue={() => router.push("/diagnosis")}
        />
      </div>
    </div>
  );
}
