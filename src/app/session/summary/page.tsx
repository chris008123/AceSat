"use client";

import { useRouter } from "next/navigation";
import StatRing from "@/components/ui/StatRing";

export default function SessionSummaryPage() {
  const router = useRouter();

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex flex-1 flex-col items-center overflow-y-auto px-5.5 pt-7.5 pb-5 text-center">
        <StatRing percent={75} label="accuracy" />

        <h1 className="font-display mt-3.5 text-[19px] font-semibold">Session complete</h1>
        <p className="mb-5.5 mt-1 max-w-[280px] text-[12.5px] leading-relaxed text-ink-soft">
          Reading Inference Practice · 5 questions
        </p>

        <div className="mb-4 flex w-full gap-2.5">
          <StatBox val="4:12" label="Time spent" />
          <StatBox val="4/5" label="Correct" up />
          <StatBox val="+13%" label="vs last time" up />
        </div>

        <div className="mb-3 flex w-full items-center gap-3 rounded-[14px] bg-primary-dim p-3.5 text-left">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary-deep)" strokeWidth={2} className="h-[18px] w-[18px] shrink-0">
            <path d="M4 19V10M11 19V5M18 19v-7" />
          </svg>
          <p className="text-[12px] leading-relaxed text-ink">
            Reading inference moved from <b className="font-semibold text-primary-deep">55% → 68%</b> —
            your biggest jump this week.
          </p>
        </div>

        <div className="mb-2 flex w-full gap-2.5 rounded-[14px] border border-line bg-paper-raised p-3.5 text-left">
          <div className="mt-0.5 flex h-[22px] w-[22px] shrink-0 items-center justify-center rounded-[7px] bg-ink">
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--gold)" strokeWidth={2} className="h-2.5 w-2.5">
              <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
            </svg>
          </div>
          <p className="text-[12px] leading-relaxed text-ink">
            You still miss questions where evidence is an <b className="font-semibold">action</b> rather
            than dialogue. I&apos;ve added a focused drill to tomorrow&apos;s plan.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-2 border-t border-line bg-paper-raised px-5.5 pt-3.5 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <button className="btn-primary" onClick={() => router.push("/dashboard")}>
          Back to dashboard
        </button>
        <button className="btn-secondary" onClick={() => router.push("/coach")}>
          Talk to coach about this session
        </button>
      </div>
    </div>
  );
}

function StatBox({ val, label, up = false }: { val: string; label: string; up?: boolean }) {
  return (
    <div className="flex-1 rounded-[14px] border border-line bg-paper-raised px-2 py-3">
      <div className={`font-mono text-[16px] font-medium ${up ? "text-primary-deep" : ""}`}>{val}</div>
      <div className="mt-0.5 text-[10.5px] text-ink-soft">{label}</div>
    </div>
  );
}
