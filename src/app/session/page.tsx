"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import QuestionCard from "@/components/session/QuestionCard";
import { api } from "@/lib/api";
import { Question } from "@/lib/types";

export default function SessionPage() {
  const router = useRouter();
  const [showExitModal, setShowExitModal] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mission, setMission] = useState<string>("");
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [finishing, setFinishing] = useState(false);
  const startedAt = useRef<number>(0);

  useEffect(() => {
    api
      .startSession()
      .then(({ sessionId, mission, questions }) => {
        setSessionId(sessionId);
        setMission(mission);
        setQuestions(questions);
        startedAt.current = Date.now();
      })
      .catch(() => setError("Couldn't load today's session. Check your connection and reload."));
  }, []);

  async function handleContinue(wasCorrect: boolean) {
    // Known simplification carried over from the mock prototype
    // (BACKEND_INTEGRATION.md §7.1): only the first question of the
    // returned set is shown before finishing, so accuracy here is
    // necessarily 100% or 0%.
    if (!sessionId) return;
    const durationSeconds = Math.round((Date.now() - startedAt.current) / 1000);
    const accuracy = wasCorrect ? 100 : 0;
    setFinishing(true);
    try {
      await api.completeSession(sessionId, accuracy, durationSeconds);
      const params = new URLSearchParams({
        accuracy: String(accuracy),
        duration: String(durationSeconds),
        mission,
      });
      router.push(`/session/summary?${params.toString()}`);
    } catch {
      setError("Couldn't save your session. Try again.");
      setFinishing(false);
    }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
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
            <span>{questions?.[0]?.topicLabel ?? mission}</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-line">
            <div className="h-full w-[20%] rounded-full bg-primary transition-all duration-500" />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-1">
        {error && <p className="mt-4 text-center text-[13px] text-warm-deep">{error}</p>}
        {!error && !questions && (
          <p className="mt-8 text-center text-[13px] text-ink-soft">Loading your session…</p>
        )}
        {questions && questions[0] && (
          <QuestionCard
            question={questions[0]}
            continueLabel={finishing ? "Saving…" : "Finish session"}
            onContinue={handleContinue}
          />
        )}
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
