"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import QuestionCard from "@/components/session/QuestionCard";
import { api } from "@/lib/api";
import { Question } from "@/lib/types";

export default function AssessmentPage() {
  const router = useRouter();
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [finishing, setFinishing] = useState(false);
  const startedAt = useRef<number>(0);

  useEffect(() => {
    api
      .startAssessment()
      .then(({ assessmentId, questions }) => {
        setAssessmentId(assessmentId);
        setQuestions(questions);
        startedAt.current = Date.now();
      })
      .catch(() => setError("Couldn't load your diagnostic questions. Check your connection and reload."));
  }, []);

  async function handleContinue(_wasCorrect: boolean, selectedLetter: string) {
    // Known simplification carried over from the mock prototype
    // (BACKEND_INTEGRATION.md §7.1): this demo only shows the first
    // returned question, not the full diagnostic set, even though a
    // real assessment normally has ~10 questions.
    if (!assessmentId || !questions) return;
    const question = questions[0];
    const timeTaken = Math.round((Date.now() - startedAt.current) / 1000);
    setFinishing(true);
    try {
      await api.submitAssessmentAnswer(assessmentId, question.id, selectedLetter, timeTaken);
      await api.completeAssessment(assessmentId);
      router.push("/diagnosis");
    } catch {
      setError("Couldn't save your answer. Try again.");
      setFinishing(false);
    }
  }

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
            <span>{questions?.[0]?.topicLabel ?? ""}</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-line">
            <div className="h-full w-[12%] rounded-full bg-primary transition-all duration-500" />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-1">
        {error && <p className="mt-4 text-center text-[13px] text-warm-deep">{error}</p>}
        {!error && !questions && (
          <p className="mt-8 text-center text-[13px] text-ink-soft">Loading your diagnostic…</p>
        )}
        {questions && questions[0] && (
          <QuestionCard
            question={questions[0]}
            continueLabel={finishing ? "Saving…" : "See my results"}
            onContinue={handleContinue}
          />
        )}
      </div>
    </div>
  );
}
