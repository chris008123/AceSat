"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import QuestionCard from "@/components/session/QuestionCard";
import { getQuestionSet } from "@/lib/questions";

export default function SessionPage() {
  const router = useRouter();
  const [showExitModal, setShowExitModal] = useState(false);
  const question = getQuestionSet("reading")[0];

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex items-center gap-3 px-5 pt-4.5 pb-2">
        <button
          onClick={() => setShowExitModal(true)}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line bg-paper-raised text-ink-soft"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3 w-3">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
        <div className="flex-1">
          <div className="mb-1.5 flex justify-between font-mono text-[11px] text-ink-soft">
            <span>Question 1 of 5</span>
            <span>Reading Inference</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-line">
            <div className="h-full w-[20%] rounded-full bg-primary transition-all duration-500" />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-1">
        <QuestionCard
          question={question}
          continueLabel="Finish session"
          onContinue={() => router.push("/session/summary")}
        />
      </div>

      {showExitModal && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-[rgba(24,35,56,0.45)] p-6">
          <div className="w-full rounded-[22px] bg-paper-raised p-5.5 shadow-lg">
            <h3 className="font-display mb-1.5 text-[17px] font-semibold">Leave this session?</h3>
            <p className="mb-4.5 text-[12.5px] leading-relaxed text-ink-soft">
              You&apos;re 1 of 5 questions in. Your progress on this set won&apos;t be saved if you
              leave now.
            </p>
            <div className="flex gap-2.5">
              <button
                onClick={() => setShowExitModal(false)}
                className="flex-1 rounded-full border border-line bg-paper py-2.5 text-[13px] font-semibold text-ink"
              >
                Keep going
              </button>
              <button
                onClick={() => router.push("/learning")}
                className="flex-1 rounded-full bg-warm py-2.5 text-[13px] font-semibold text-white"
              >
                Leave
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
