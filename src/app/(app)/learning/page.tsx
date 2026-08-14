"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, StudyPlanItem } from "@/lib/api";

export default function LearningHubPage() {
  const [plan, setPlan] = useState<StudyPlanItem[] | null>(null);

  useEffect(() => {
    api
      .studyPlan()
      .then((res) => setPlan(res.plan))
      .catch(() => setPlan([]));
  }, []);

  const mission = plan?.[0];

  return (
    <div className="flex flex-col gap-4 px-4.5 py-5">
      <div>
        <h1 className="font-display text-[19px] font-semibold">Learning</h1>
        <p className="mt-0.5 text-[12.5px] text-ink-soft">
          Practice sessions and coach check-ins live here
        </p>
      </div>

      <Link href="/session" className="card flex items-center gap-3.5">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-dim text-primary-deep">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="h-5 w-5">
            <path d="M5 4h11a2 2 0 0 1 2 2v14l-7.5-4L5 20V4Z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-display text-[14px] font-semibold">Today&apos;s mission</h3>
          <p className="mt-0.5 text-[11.5px] text-ink-soft">
            {mission ? `${mission.topic} · ${mission.time}` : "General practice"}
          </p>
        </div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3.5 w-3.5 shrink-0 text-ink-soft">
          <path d="M9 6l6 6-6 6" />
        </svg>
      </Link>

      <Link href="/coach" className="card flex items-center gap-3.5">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gold-dim text-[#8A5A12]">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="h-5 w-5">
            <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-display text-[14px] font-semibold">Message your coach</h3>
          <p className="mt-0.5 text-[11.5px] text-ink-soft">Get a personalized study insight</p>
        </div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3.5 w-3.5 shrink-0 text-ink-soft">
          <path d="M9 6l6 6-6 6" />
        </svg>
      </Link>
    </div>
  );
}
