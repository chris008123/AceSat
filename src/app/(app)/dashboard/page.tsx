"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { api, DashboardResponse, StudyPlanItem } from "@/lib/api";
import { getLocalName, getLastShownMilestone, setLastShownMilestone } from "@/lib/studentStore";
import { fadeSlideUpStagger } from "@/lib/motion";
import { SkeletonCard, SkeletonLine } from "@/components/ui/Skeleton";
import StreakMilestone from "@/components/ui/StreakMilestone";

const MILESTONES = [7, 14, 30, 60, 100, 150, 200, 365];

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [plan, setPlan] = useState<StudyPlanItem[] | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [milestoneToShow, setMilestoneToShow] = useState<number | null>(null);
  const name = getLocalName() ?? "there";

  useEffect(() => {
    let cancelled = false;
    Promise.allSettled([
      api.getDashboard().catch(() => null),
      api
        .studyPlan()
        .then((res) => res.plan)
        .catch(() => [] as StudyPlanItem[]),
    ]).then(([dashboardResult, planResult]) => {
      if (cancelled) return;
      const dashboardData = dashboardResult.status === "fulfilled" ? dashboardResult.value : null;
      setDashboard(dashboardData);
      setPlan(planResult.status === "fulfilled" ? planResult.value : []);
      setLoaded(true);

      if (dashboardData) {
        const streak = dashboardData.streak ?? 0;
        const lastShown = getLastShownMilestone();
        const reached = MILESTONES.filter((m) => m <= streak && m > lastShown).pop();
        if (reached) setMilestoneToShow(reached);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  function dismissMilestone() {
    if (milestoneToShow) setLastShownMilestone(milestoneToShow);
    setMilestoneToShow(null);
  }

  const mission = plan?.[0];

  return (
    <div className="relative flex flex-col gap-4 px-4.5 py-5">
      <StreakMilestone
        show={!!milestoneToShow}
        streak={milestoneToShow ?? 0}
        onDismiss={dismissMilestone}
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-[19px] font-semibold">Good to see you, {name}</h1>
          {loaded ? (
            <p className="mt-0.5 text-[12.5px] text-ink-soft">
              {dashboard?.weak_area
                ? `${dashboard.weak_area} is your biggest opportunity today`
                : "Let's keep building momentum"}
            </p>
          ) : (
            <SkeletonLine width="180px" height={10} className="mt-1.5" />
          )}
        </div>
        <div className="flex shrink-0 items-center gap-1.5 rounded-full bg-gold-dim px-3 py-1.5 font-mono text-[12px] font-medium text-[#8A5A12]">
          🔥 {dashboard?.streak ?? 0} days
        </div>
      </div>

      {!loaded ? (
        <>
          <SkeletonCard lines={2} />
          <div className="grid grid-cols-2 gap-3.5">
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
          </div>
        </>
      ) : (
        <>
          <motion.div variants={fadeSlideUpStagger} initial="initial" animate="animate" custom={0}>
            <Link href="/session" className="card flex flex-col gap-3">
              <div className="eyebrow">Today&apos;s mission</div>
              <div className="flex items-start justify-between gap-2.5">
                <div>
                  <h2 className="font-display text-[17px] font-semibold">
                    {mission?.topic ?? "General Practice"}
                  </h2>
                  <p className="mt-1 text-[12.5px] text-ink-soft">
                    {mission?.reason ?? "A quick warm-up session to keep your streak going"}
                  </p>
                </div>
                <div className="font-mono text-[12px] whitespace-nowrap text-ink-soft">
                  {mission?.time ?? "15 min"}
                </div>
              </div>
              <span className="btn-primary text-center">Start session</span>
            </Link>
          </motion.div>

          <div className="grid grid-cols-2 gap-3.5">
            <motion.div variants={fadeSlideUpStagger} initial="initial" animate="animate" custom={1} className="card">
              <div className="eyebrow mb-2.5">Progress</div>
              <div className="flex flex-col gap-2 text-[12.5px] text-ink-soft">
                <div className="flex justify-between">
                  <span>Estimated score</span>
                  <span className="font-mono text-ink">{dashboard?.current_score ?? "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span>Change</span>
                  <span className="font-mono text-ink">{dashboard?.improvement ?? "—"}</span>
                </div>
              </div>
            </motion.div>

            <motion.div variants={fadeSlideUpStagger} initial="initial" animate="animate" custom={2}>
              <Link href="/coach" className="card block h-full">
                <div className="eyebrow mb-2.5">Coach note</div>
                <p className="mb-3 text-[13px] leading-relaxed text-ink">
                  {plan && plan.length > 0
                    ? plan[0].reason
                    : "Ask your coach anything about what to focus on next."}
                </p>
                <span className="inline-flex items-center gap-1 text-[12.5px] font-semibold text-primary-deep">
                  Review with Coach →
                </span>
              </Link>
            </motion.div>
          </div>
        </>
      )}
    </div>
  );
}
