/**
 * Shared motion language for AceMentor AI — the animation equivalent of
 * the color/type tokens in globals.css. Import these instead of writing
 * one-off durations/easings per component, so every animation in the app
 * feels like it belongs to the same system.
 */

export const duration = {
  fast: 0.12,
  base: 0.22,
  slow: 0.4,
} as const;

// A gentle "settle" curve — quick start, soft landing. Used almost
// everywhere instead of linear/ease so motion feels considered rather
// than mechanical.
export const easeSettle = [0.32, 0.72, 0, 1] as const;

export const tapScale = {
  whileTap: { scale: 0.97 },
  transition: { duration: duration.fast },
};

export const fadeSlideUp = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: duration.base, ease: easeSettle },
};

/** For lists of cards — pass `custom={index}` on each item. */
export const fadeSlideUpStagger = {
  initial: { opacity: 0, y: 10 },
  animate: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: duration.base, ease: easeSettle, delay: i * 0.06 },
  }),
};

/** Parent/child pair for staggering a fixed list of cards without
 * hand-numbering `custom` indices — wrap the list in
 * `<motion.div variants={staggerParent} initial="hidden" animate="visible">`
 * and each child in `<motion.div variants={staggerItem}>`. */
export const staggerParent = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07 } },
};

export const staggerItem = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: duration.base, ease: easeSettle } },
};

export const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: { duration: duration.base, ease: easeSettle },
};
