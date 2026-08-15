"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ConfidenceLevel,
  EXAM_TIMELINE_LABELS,
  OnboardingAnswers,
  STUDY_TIME_LABELS,
} from "@/lib/types";
import { saveLocalName } from "@/lib/studentStore";
import { api, ApiError } from "@/lib/api";

const TOTAL_STEPS = 6;

const SCORE_OPTIONS = [
  { val: "1200", n: "1200", l: "Solid" },
  { val: "1300", n: "1300", l: "Competitive" },
  { val: "1400", n: "1400", l: "Strong" },
  { val: "1500", n: "1500+", l: "Top tier" },
];

const DATE_OPTIONS: { val: OnboardingAnswers["examTimeline"]; t: string; s: string }[] = [
  { val: "1month", t: "Within 1 month", s: "Intensive pace" },
  { val: "3months", t: "2–3 months", s: "Steady pace" },
  { val: "6months", t: "4–6 months", s: "Relaxed pace" },
];

const TIME_OPTIONS: { val: OnboardingAnswers["dailyStudyTime"]; t: string; s: string }[] = [
  { val: "20", t: "15–20 minutes", s: "Quick daily habit" },
  { val: "45", t: "30–45 minutes", s: "Balanced pace" },
  { val: "60", t: "1 hour+", s: "Fast progress" },
];

const CONF_OPTIONS: { val: ConfidenceLevel; emoji: string; t: string; s: string }[] = [
  { val: "low", emoji: "😟", t: "Not very confident", s: "Let's build from the basics" },
  { val: "mid", emoji: "🙂", t: "Somewhat confident", s: "I know some areas need work" },
  { val: "high", emoji: "😀", t: "Pretty confident", s: "I mostly need refinement" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [answers, setAnswers] = useState<OnboardingAnswers>({
    name: "",
    targetScore: null,
    examTimeline: null,
    dailyStudyTime: null,
    confidence: null,
  });

  const canContinue =
    step === 1
      ? answers.name.trim().length > 0
      : step === 2
      ? !!answers.targetScore
      : step === 3
      ? true // exam date is optional — defaults to "Flexible"
      : step === 4
      ? !!answers.dailyStudyTime
      : step === 5
      ? !!answers.confidence
      : true;

  async function handleContinue() {
    if (step < TOTAL_STEPS) {
      setStep(step + 1);
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      await api.createProfile(answers);
      saveLocalName(answers.name);
      router.push("/assessment");
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Couldn't save your profile — try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      {/* top bar: back + progress dots */}
      <div className="flex items-center gap-3 px-5 pt-4.5 pb-2">
        <button
          onClick={() => setStep((s) => Math.max(1, s - 1))}
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line bg-paper-raised text-ink-soft ${
            step === 1 ? "invisible" : ""
          }`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3.5 w-3.5">
            <path d="M15 6l-6 6 6 6" />
          </svg>
        </button>
        <div className="flex flex-1 gap-1.5">
          {Array.from({ length: TOTAL_STEPS }).map((_, i) => (
            <div key={i} className="h-1 flex-1 overflow-hidden rounded-full bg-line">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: i < step ? "100%" : "0%" }}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-y-auto px-6 pb-5 pt-1">
        {step === 1 && (
          <Step eyebrow="Step 1 of 6" title="What should we call you?" sub="This is how your coach will greet you every day.">
            <div className="flex flex-col gap-2">
              <label className="text-[12px] font-semibold text-ink-soft">Your name</label>
              <input
                autoFocus
                type="text"
                placeholder="e.g. Sarah"
                value={answers.name}
                onChange={(e) => setAnswers({ ...answers, name: e.target.value })}
                className="rounded-[14px] border-[1.5px] border-line bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary"
              />
            </div>
          </Step>
        )}

        {step === 2 && (
          <Step eyebrow="Step 2 of 6" title="What's your target SAT score?" sub="We'll build your whole plan around closing this gap.">
            <div className="grid grid-cols-2 gap-2.5">
              {SCORE_OPTIONS.map((opt) => {
                const selected = answers.targetScore === opt.val;
                return (
                  <button
                    key={opt.val}
                    onClick={() => setAnswers({ ...answers, targetScore: opt.val })}
                    className={`rounded-[14px] border-[1.5px] bg-paper-raised p-3.5 text-center ${
                      selected ? "border-primary bg-primary-dim" : "border-line"
                    }`}
                  >
                    <div className={`font-mono text-[19px] font-medium ${selected ? "text-primary-deep" : ""}`}>
                      {opt.n}
                    </div>
                    <div className="mt-0.5 text-[10.5px] text-ink-soft">{opt.l}</div>
                  </button>
                );
              })}
            </div>
          </Step>
        )}

        {step === 3 && (
          <Step
            eyebrow="Step 3 of 6"
            title="When's your exam?"
            sub="This sets the pace of your study plan — skip if you're not sure yet."
          >
            <div className="flex flex-col gap-2.5">
              {DATE_OPTIONS.map((opt) => {
                const selected = answers.examTimeline === opt.val;
                return (
                  <button
                    key={opt.val}
                    onClick={() => setAnswers({ ...answers, examTimeline: opt.val })}
                    className={`flex items-center justify-between rounded-[14px] border-[1.5px] bg-paper-raised px-4 py-3.5 text-left ${
                      selected ? "border-primary bg-primary-dim" : "border-line"
                    }`}
                  >
                    <div>
                      <div className="text-[13.5px] font-semibold">{opt.t}</div>
                      <div className="mt-0.5 text-[11.5px] text-ink-soft">{opt.s}</div>
                    </div>
                    <div
                      className={`relative h-5 w-5 shrink-0 rounded-full border-[1.5px] ${
                        selected ? "border-primary" : "border-line"
                      }`}
                    >
                      {selected && (
                        <div className="absolute inset-[3.5px] rounded-full bg-primary" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
            <p className="mt-3 text-center text-[11.5px] text-ink-soft">
              No pressure — this defaults to flexible if you skip it.
            </p>
          </Step>
        )}

        {step === 4 && (
          <Step
            eyebrow="Step 4 of 6"
            title="How much time can you study daily?"
            sub="Be realistic — a short daily session beats an occasional long one."
          >
            <div className="flex flex-col gap-2.5">
              {TIME_OPTIONS.map((opt) => {
                const selected = answers.dailyStudyTime === opt.val;
                return (
                  <button
                    key={opt.val}
                    onClick={() => setAnswers({ ...answers, dailyStudyTime: opt.val })}
                    className={`flex items-center gap-3 rounded-[14px] border-[1.5px] bg-paper-raised px-3.5 py-3.5 text-left ${
                      selected ? "border-primary bg-primary-dim" : "border-line"
                    }`}
                  >
                    <div className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-[10px] bg-gold-dim text-[#8A5A12]">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-4 w-4">
                        <circle cx="12" cy="12" r="9" />
                        <path d="M12 7v5l3 3" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-[13.5px] font-semibold">{opt.t}</div>
                      <div className="text-[11.5px] text-ink-soft">{opt.s}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </Step>
        )}

        {step === 5 && (
          <Step
            eyebrow="Step 5 of 6"
            title="How confident do you feel right now?"
            sub="No wrong answer — this helps your coach start in the right place."
          >
            <div className="flex flex-col gap-2.5">
              {CONF_OPTIONS.map((opt) => {
                const selected = answers.confidence === opt.val;
                return (
                  <button
                    key={opt.val}
                    onClick={() => setAnswers({ ...answers, confidence: opt.val })}
                    className={`flex items-center gap-3.5 rounded-[14px] border-[1.5px] bg-paper-raised p-4 text-left ${
                      selected ? "border-primary bg-primary-dim" : "border-line"
                    }`}
                  >
                    <span className="text-[22px]">{opt.emoji}</span>
                    <div>
                      <div className="text-[13.5px] font-semibold">{opt.t}</div>
                      <div className="text-[11.5px] text-ink-soft">{opt.s}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </Step>
        )}

        {step === 6 && (
          <div className="flex flex-1 flex-col items-center justify-center text-center">
            <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-[18px] bg-ink">
              <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2} className="h-7 w-7">
                <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
              </svg>
            </div>
            <h1 className="font-display text-[20px] font-semibold">
              You&apos;re all set, {answers.name || "there"}
            </h1>
            <p className="mt-1.5 max-w-[270px] text-[13px] leading-relaxed text-ink-soft">
              Next, a short assessment helps me understand exactly where to start.
            </p>
            <div className="mt-5.5 w-full rounded-[14px] border border-line bg-paper-raised p-4 text-left">
              <SummaryRow k="Target score" v={answers.targetScore ?? "—"} />
              <SummaryRow
                k="Exam timeline"
                v={answers.examTimeline ? EXAM_TIMELINE_LABELS[answers.examTimeline] : "Flexible"}
              />
              <SummaryRow
                k="Daily study time"
                v={answers.dailyStudyTime ? STUDY_TIME_LABELS[answers.dailyStudyTime] : "—"}
                last
              />
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-line bg-paper-raised px-6 pt-3.5 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        {submitError && (
          <p className="mb-2 text-center text-[12px] text-warm-deep">{submitError}</p>
        )}
        <button className="btn-primary" disabled={!canContinue || submitting} onClick={handleContinue}>
          {submitting ? "Setting up…" : step === TOTAL_STEPS ? "Start assessment" : "Continue"}
        </button>
      </div>
    </div>
  );
}

function Step({
  eyebrow,
  title,
  sub,
  children,
}: {
  eyebrow: string;
  title: string;
  sub: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="eyebrow mb-3.5">{eyebrow}</div>
      <h1 className="font-display mb-2 text-[22px] font-semibold leading-snug">{title}</h1>
      <p className="mb-6 text-[13px] leading-relaxed text-ink-soft">{sub}</p>
      {children}
    </div>
  );
}

function SummaryRow({ k, v, last = false }: { k: string; v: string; last?: boolean }) {
  return (
    <div className={`flex justify-between py-1.5 text-[12.5px] ${last ? "" : "border-b border-line"}`}>
      <span className="text-ink-soft">{k}</span>
      <span className="font-mono font-semibold">{v}</span>
    </div>
  );
}
