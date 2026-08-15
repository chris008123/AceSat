"use client";

import { AnimatePresence, motion } from "framer-motion";
import CoachMark from "./CoachMark";

interface StreakMilestoneProps {
  show: boolean;
  streak: number;
  onDismiss: () => void;
}

const MILESTONE_COPY: Record<number, string> = {
  7: "One full week of showing up. That consistency is exactly what moves a score.",
  14: "Two weeks straight — the habit is sticking, and so is the progress.",
  30: "A full month of daily practice. This is what real improvement looks like.",
  60: "Two months in. Most students don't make it this far — you have.",
  100: "100 days. At this point, studying isn't the hard part anymore — it's just what you do.",
};

// A handful of small gold particles that burst outward and fade —
// deliberately restrained (6, not 30) so it reads as a polished accent
// rather than confetti-spam. Gold stays reserved for exactly this kind
// of achievement moment per the design system.
const PARTICLES = Array.from({ length: 6 }, (_, i) => {
  const angle = (i / 6) * Math.PI * 2;
  return {
    x: Math.cos(angle) * 70,
    y: Math.sin(angle) * 70,
    delay: 0.15 + i * 0.03,
  };
});

export default function StreakMilestone({ show, streak, onDismiss }: StreakMilestoneProps) {
  const copy = MILESTONE_COPY[streak] ?? `${streak} days of consistent practice. Keep this going.`;

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="absolute inset-0 z-50 flex items-center justify-center bg-[rgba(24,35,56,0.55)] p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="relative flex w-full flex-col items-center rounded-[22px] bg-paper-raised p-7 text-center shadow-lg"
            initial={{ opacity: 0, scale: 0.9, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 8 }}
            transition={{ type: "spring", stiffness: 300, damping: 24 }}
          >
            <div className="relative mb-4 flex h-[110px] w-[110px] items-center justify-center">
              {PARTICLES.map((p, i) => (
                <motion.span
                  key={i}
                  className="absolute h-1.5 w-1.5 rounded-full bg-gold"
                  initial={{ x: 0, y: 0, opacity: 0 }}
                  animate={{ x: p.x, y: p.y, opacity: [0, 1, 0] }}
                  transition={{ duration: 0.9, delay: p.delay, ease: "easeOut" }}
                />
              ))}
              <motion.div
                initial={{ scale: 0.4, rotate: -20 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 260, damping: 14, delay: 0.1 }}
              >
                <CoachMark size={90} />
              </motion.div>
            </div>

            <div className="font-mono text-[13px] font-medium text-gold">🔥 {streak}-day streak</div>
            <h2 className="font-display mt-1 text-[20px] font-semibold">You&apos;re on a roll</h2>
            <p className="mt-2 max-w-[260px] text-[13px] leading-relaxed text-ink-soft">{copy}</p>

            <button className="btn-primary mt-5" onClick={onDismiss}>
              Keep going
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
