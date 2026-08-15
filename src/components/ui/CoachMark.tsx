"use client";

import { motion } from "framer-motion";

interface CoachMarkProps {
  size?: number;
  /** Idle bob/tilt loop — use on the coach avatar and splash, skip on tiny inline icons. */
  animated?: boolean;
  /** Small green "active" dot in the corner, like a presence indicator. */
  showPulse?: boolean;
  className?: string;
}

/**
 * The dolphin is built from the same leaping-arc geometry as the splash
 * mark (an arc from lower-left to upper-right) — it's the growth-arc
 * motif literally taking shape as a leap, not a separate mascot bolted
 * onto the brand. Dimensional feel comes from an SVG gradient (simulated
 * top-lit surface) + drop shadow + a subtle CSS 3D tilt loop — no WebGL,
 * so it stays cheap on low-end devices per the accessibility principles
 * in Product_features.txt.
 */
export default function CoachMark({
  size = 40,
  animated = true,
  showPulse = false,
  className = "",
}: CoachMarkProps) {
  return (
    <div
      className={`relative ${className}`}
      style={{ width: size, height: size, perspective: 300 }}
    >
      <motion.div
        style={{ width: size, height: size, transformStyle: "preserve-3d" }}
        animate={
          animated
            ? { rotateY: [-8, 8, -8], rotateX: [2, -2, 2], y: [0, -2, 0] }
            : undefined
        }
        transition={
          animated
            ? { duration: 5, repeat: Infinity, ease: "easeInOut" }
            : undefined
        }
        whileTap={{ scale: 0.92, rotateZ: -6 }}
      >
        <svg viewBox="0 0 74 74" width={size} height={size} style={{ overflow: "visible" }}>
          <defs>
            <linearGradient id="dolphinBody" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#38C088" />
              <stop offset="55%" stopColor="var(--primary)" />
              <stop offset="100%" stopColor="var(--primary-deep)" />
            </linearGradient>
            <filter id="dolphinShadow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="3" stdDeviation="3" floodColor="#0F3D28" floodOpacity="0.28" />
            </filter>
          </defs>

          <g filter="url(#dolphinShadow)">
            {/* leaping body — same arc math as the splash mark's growth-arc */}
            <path
              d="M14,54 A30,30 0 0 1 58,16"
              fill="none"
              stroke="url(#dolphinBody)"
              strokeWidth="10"
              strokeLinecap="round"
            />
            {/* dorsal fin, sitting on the outer edge of the arc */}
            <path
              d="M38,26 C40,17 47,13 53,13 C48,18 46,24 45,29 Z"
              fill="var(--primary-deep)"
            />
            {/* tail flukes */}
            <path
              d="M14,54 C7,53 2,57 0,63 C6,61 10,63 13,67 C13,61 14,57 14,54 Z"
              fill="var(--primary)"
            />
            {/* eye / snout tip — the one gold accent, echoing the splash spark */}
            <circle cx="60" cy="15" r="3.4" fill="var(--gold)" />
          </g>
        </svg>
      </motion.div>

      {showPulse && (
        <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-paper-raised bg-primary" />
      )}
    </div>
  );
}
