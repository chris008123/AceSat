"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, DiagnoseResponse } from "@/lib/api";

export default function DiagnosisPage() {
  const router = useRouter();
  const [diagnosis, setDiagnosis] = useState<DiagnoseResponse | null>(null);

  useEffect(() => {
    api
      .diagnose()
      .then(setDiagnosis)
      .catch(() =>
        // Known limitation: the assessment page above only answers one
        // question (BACKEND_INTEGRATION.md §7.1), so there often isn't
        // enough evidence yet for the AI bridge's weak/strong-topic
        // detection (min 3 answers per topic) — this shows a graceful
        // fallback rather than an error in that case.
        setDiagnosis({
          weaknesses: [],
          strengths: [],
          recommendation: "Complete a few more questions and I'll be able to spot patterns here.",
        })
      );
  }, []);

  const cards = diagnosis
    ? [
        ...diagnosis.strengths.map((topic) => ({
          kind: "strength" as const,
          title: `Strength: ${topic}`,
          body: "You're already performing well here.",
        })),
        ...diagnosis.weaknesses.map((topic) => ({
          kind: "weakness" as const,
          title: `Focus area: ${topic}`,
          body: "This is where we'll start building your study plan.",
        })),
      ]
    : [];

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
            {diagnosis?.recommendation ?? "Based on your diagnostic, here's where we'll start."}
          </p>

          {!diagnosis && (
            <p className="mt-6 text-[13px] text-ink-soft">Analyzing your answers…</p>
          )}

          {diagnosis && cards.length === 0 && (
            <p className="mt-6 text-[13px] text-ink-soft">
              Not enough data yet for a detailed breakdown — keep practicing and this will fill in.
            </p>
          )}

          <div className="mt-4.5 flex w-full flex-col gap-2.5 text-left">
            {cards.map((c) => (
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
