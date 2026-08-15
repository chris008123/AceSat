"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import StatRing from "@/components/ui/StatRing";

function SessionSummaryContent() {
  const router = useRouter();
  const params = useSearchParams();

  const accuracy = Number(params.get("accuracy") ?? "0");
  const durationSeconds = Number(params.get("duration") ?? "0");
  const mission = params.get("mission") || "Practice session";
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = durationSeconds % 60;
  const timeSpent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
  const isGoodOutcome = accuracy >= 60;

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      <div className="flex flex-1 flex-col items-center overflow-y-auto px-5.5 pt-7.5 pb-5 text-center">
        <StatRing percent={accuracy} label="accuracy" />

        <h1 className="font-display mt-3.5 text-[19px] font-semibold">Session complete</h1>
        <p className="mb-5.5 mt-1 max-w-[280px] text-[12.5px] leading-relaxed text-ink-soft">
          {mission}
        </p>

        <div className="mb-4 flex w-full gap-2.5">
          <StatBox val={timeSpent} label="Time spent" />
          <StatBox val={accuracy >= 100 ? "1/1" : "0/1"} label="Correct" up={isGoodOutcome} />
          <StatBox val={`${accuracy}%`} label="Accuracy" up={isGoodOutcome} />
        </div>

        {isGoodOutcome ? (
          <div className="mb-3 flex w-full items-center gap-3 rounded-[14px] bg-primary-dim p-3.5 text-left">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--primary-deep)"
              strokeWidth={2}
              className="h-[18px] w-[18px] shrink-0"
            >
              <path d="M4 19V10M11 19V5M18 19v-7" />
            </svg>
            <p className="text-[12px] leading-relaxed text-ink">
              Nice work — that&apos;s a strong result. Keep this pace going.
            </p>
          </div>
        ) : (
          <div className="mb-3 flex w-full items-center gap-3 rounded-[14px] bg-warm-dim p-3.5 text-left">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--warm-deep)"
              strokeWidth={2}
              className="h-[18px] w-[18px] shrink-0"
            >
              <path d="M12 8v5M12 16h.01" />
              <circle cx="12" cy="12" r="9" />
            </svg>
            <p className="text-[12px] leading-relaxed text-ink">
              Not your best round — let&apos;s go over this one with your coach so it sticks next time.
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2 border-t border-line bg-paper-raised px-5.5 pt-3.5 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <button
          className={isGoodOutcome ? "btn-primary" : "btn-secondary"}
          onClick={() => router.push("/dashboard")}
        >
          Back to dashboard
        </button>
        <button
          className={isGoodOutcome ? "btn-secondary" : "btn-primary"}
          onClick={() => router.push("/coach")}
        >
          Talk to coach about this session
        </button>
      </div>
    </div>
  );
}

export default function SessionSummaryPage() {
  return (
    <Suspense fallback={null}>
      <SessionSummaryContent />
    </Suspense>
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
