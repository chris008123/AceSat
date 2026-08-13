"use client";

import { useRouter } from "next/navigation";

const CARDS = [
  {
    kind: "strength" as const,
    title: "Strength: Vocabulary",
    body: "You're already performing above target level here.",
  },
  {
    kind: "weakness" as const,
    title: "Focus area: Reading inference",
    body: "Missed evidence-based questions tied to character action.",
  },
  {
    kind: "weakness" as const,
    title: "Focus area: Algebra word problems",
    body: "Setup/translation is the gap, not the calculation itself.",
  },
];

export default function DiagnosisPage() {
  const router = useRouter();

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-8 pb-5">
        <div className="flex flex-1 flex-col items-center text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-ink">
            <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2} className="h-6 w-6">
              <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
            </svg>
          </div>
          <h1 className="font-display text-[19px] font-semibold">Your learning profile</h1>
          <p className="mt-1.5 max-w-[270px] text-[12.5px] leading-relaxed text-ink-soft">
            Based on your diagnostic, here&apos;s where we&apos;ll start.
          </p>

          <div className="mt-4.5 flex w-full flex-col gap-2.5 text-left">
            {CARDS.map((c) => (
              <div
                key={c.title}
                className="flex items-start gap-2.5 rounded-[14px] border border-line bg-paper-raised p-3.5"
              >
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-[7px] ${
                    c.kind === "strength"
                      ? "bg-primary-dim text-primary-deep"
                      : "bg-warm-dim text-warm-deep"
                  }`}
                >
                  {c.kind === "strength" ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-3 w-3">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} className="h-3 w-3">
                      <path d="M12 8v5M12 16h.01" />
                      <circle cx="12" cy="12" r="9" />
                    </svg>
                  )}
                </div>
                <div>
                  <div className="text-[13px] font-semibold">{c.title}</div>
                  <div className="mt-0.5 text-[11.5px] leading-relaxed text-ink-soft">{c.body}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-line bg-paper-raised px-6 pt-3.5 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <button className="btn-primary" onClick={() => router.push("/dashboard")}>
          Build my study plan
        </button>
      </div>
    </div>
  );
}
