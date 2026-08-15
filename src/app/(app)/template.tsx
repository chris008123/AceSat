"use client";

import { motion } from "framer-motion";
import { pageTransition } from "@/lib/motion";

/**
 * Scoped to (app)/ deliberately, not the app root: Next.js remounts
 * everything under a template on each navigation. A root-level template
 * would remount (app)/layout.tsx too, causing BottomNav to flicker on
 * every tab switch. Scoping it here means BottomNav (defined in
 * (app)/layout.tsx, outside this template) stays mounted and static
 * while only the tab content transitions.
 */
export default function AppTemplate({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={pageTransition.initial}
      animate={pageTransition.animate}
      transition={pageTransition.transition}
    >
      {children}
    </motion.div>
  );
}
