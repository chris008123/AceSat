"use client";

import { motion } from "framer-motion";
import { fadeSlideUpStagger } from "@/lib/motion";

interface AnimatedCardProps {
  children: React.ReactNode;
  index?: number;
  className?: string;
}

/** Drop-in wrapper for anything using the `.card` class — fades and
 * lifts in on mount, staggered by `index` when rendering a list. */
export default function AnimatedCard({ children, index = 0, className = "" }: AnimatedCardProps) {
  return (
    <motion.div
      className={`card ${className}`}
      custom={index}
      initial="initial"
      animate="animate"
      variants={fadeSlideUpStagger}
    >
      {children}
    </motion.div>
  );
}
