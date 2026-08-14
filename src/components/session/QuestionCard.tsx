"use client";

import { useState } from "react";
import { Question } from "@/lib/types";

interface QuestionCardProps {
  question: Question;
  onContinue: (wasCorrect: boolean, selectedLetter: string) => void;
  continueLabel?: string;
}

export default function QuestionCard({
  question,
  onContinue,
  continueLabel = "Continue",
}: QuestionCardProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const isCorrect = selected === question.correctLetter;

  function handleSelect(letter: string) {
    if (submitted) return;
    setSelected(letter);
    setSubmitted(true);
  }

  return (
    <div className="relative flex flex-1 flex-col pb-24">
      <span className="eyebrow">📘 {question.topicLabel}</span>

      <h2 className="font-display mt-3 text-[19px] font-medium leading-snug">
        {question.prompt}
      </h2>

      {question.passage && (
        <div className="mt-3 rounded-[14px] border border-line bg-paper-raised p-4 text-[13px] leading-relaxed text-ink-soft">
          {question.passage}
        </div>
      )}

      <div className="mt-4 flex flex-col gap-2.5">
        {question.options.map((opt) => {
          const isSelected = selected === opt.letter;
          const showCorrect = submitted && opt.letter === question.correctLetter;
          const showIncorrect = submitted && isSelected && !isCorrect;

          return (
            <button
              key={opt.letter}
              onClick={() => handleSelect(opt.letter)}
              disabled={submitted}
              className={`flex items-center gap-3 rounded-[14px] border-[1.5px] bg-paper-raised px-3.5 py-3.5 text-left transition-colors ${
                showCorrect
                  ? "border-primary bg-primary-dim"
                  : showIncorrect
                  ? "border-warm bg-warm-dim"
                  : isSelected
                  ? "border-primary bg-primary-dim"
                  : "border-line hover:border-[#C7CEE0]"
              }`}
            >
              <span
                className={`flex h-[26px] w-[26px] shrink-0 items-center justify-center rounded-full border-[1.5px] font-mono text-[12px] font-medium ${
                  showCorrect
                    ? "border-primary bg-primary text-white"
                    : showIncorrect
                    ? "border-warm bg-warm text-white"
                    : isSelected
                    ? "border-primary bg-primary text-white"
                    : "border-line bg-paper text-ink-soft"
                }`}
              >
                {opt.letter}
              </span>
              <span className="text-[13.5px] text-ink">{opt.text}</span>
            </button>
          );
        })}
      </div>

      {/* feedback panel */}
      <div
        className={`absolute inset-x-0 bottom-0 rounded-t-[22px] border-t border-line bg-paper-raised p-5 shadow-[0_-10px_30px_-14px_rgba(24,35,56,0.25)] transition-transform duration-400 ${
          submitted ? "translate-y-0" : "translate-y-full"
        }`}
      >
        <div className="mb-2.5 flex items-center gap-2.5">
          <div
            className={`flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full text-white ${
              isCorrect ? "bg-primary" : "bg-warm"
            }`}
          >
            {isCorrect ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-[15px] w-[15px]">
                <path d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-[15px] w-[15px]">
                <path d="M12 8v5M12 16h.01" />
                <circle cx="12" cy="12" r="9" />
              </svg>
            )}
          </div>
          <div>
            <div className="font-display text-[16px] font-semibold">
              {isCorrect ? "Nice work" : "Not quite"}
            </div>
            <div className="text-[11.5px] text-ink-soft">
              {isCorrect
                ? "You spotted the right evidence"
                : `The correct answer is ${question.correctLetter}`}
            </div>
          </div>
        </div>

        <div className="mb-3.5 flex gap-2.5 rounded-[14px] bg-paper p-3.5">
          <div className="mt-0.5 flex h-[22px] w-[22px] shrink-0 items-center justify-center rounded-full bg-ink">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--gold)" strokeWidth={2.5} className="h-[11px] w-[11px]">
              <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
            </svg>
          </div>
          <p className="text-[12.5px] leading-relaxed text-ink">{question.explanation}</p>
        </div>

        <button className="btn-primary" onClick={() => onContinue(isCorrect, selected ?? "")}>
          {continueLabel}
        </button>
      </div>
    </div>
  );
}
