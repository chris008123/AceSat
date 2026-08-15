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
  const [currentIndex, setCurrentIndex] = useState(0);
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
      .catch(() => {
        setError(
          "Couldn't load your diagnostic questions. Check your connection and reload."
        );
      });
  }, []);

  async function handleContinue(
    _wasCorrect: boolean,
    selectedLetter: string
  ) {
    if (!assessmentId || !questions) return;

    const question = questions[currentIndex];

    if (!question) return;

    const timeTaken = Math.round(
      (Date.now() - startedAt.current) / 1000
    );

    try {
      await api.submitAssessmentAnswer(
        assessmentId,
        question.id,
        selectedLetter,
        timeTaken
      );

      const isLastQuestion =
        currentIndex === questions.length - 1;

      if (isLastQuestion) {
        setFinishing(true);

        await api.completeAssessment(assessmentId);

        router.push("/diagnosis");
        return;
      }

      // Move to the next question.
      setCurrentIndex((previous) => previous + 1);

      // Restart timer for the next question.
      startedAt.current = Date.now();
    } catch {
      setError("Couldn't save your answer. Try again.");
      setFinishing(false);
    }
  }

  const currentQuestion = questions?.[currentIndex];

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      <div className="flex items-center gap-3 px-5 pt-4.5 pb-2">
        <button
          onClick={() => router.push("/onboarding")}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line bg-paper-raised text-ink-soft"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            className="h-3 w-3"
          >
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>

        <div className="flex-1">
          <div className="mb-1.5 flex justify-between font-mono text-[11px] text-ink-soft">
            <span>
              Question{" "}
              {questions ? currentIndex + 1 : 0} of{" "}
              {questions?.length ?? 0} · Diagnostic
            </span>

            <span>
              {currentQuestion?.topicLabel ?? ""}
            </span>
          </div>

          <div className="h-1.5 overflow-hidden rounded-full bg-line">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{
                width: questions
                  ? `${((currentIndex + 1) / questions.length) * 100}%`
                  : "0%",
              }}
            />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-1">
        {error && (
          <p className="mt-4 text-center text-[13px] text-warm-deep">
            {error}
          </p>
        )}

        {!error && !questions && (
          <p className="mt-8 text-center text-[13px] text-ink-soft">
            Loading your diagnostic…
          </p>
        )}

        {currentQuestion && (
          <QuestionCard
            key={currentQuestion.id}
            question={currentQuestion}
            continueLabel={
              finishing
                ? "Saving…"
                : currentIndex === questions!.length - 1
                  ? "See my results"
                  : "Next question"
            }
            onContinue={handleContinue}
          />
        )}
      </div>
    </div>
  );
}
