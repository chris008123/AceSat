"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Home",
    icon: (
      <>
        <path d="M4 11.5 12 4l8 7.5" />
        <path d="M6 10v9h12v-9" />
      </>
    ),
  },
  {
    href: "/learning",
    label: "Learning",
    icon: <path d="M5 4h11a2 2 0 0 1 2 2v14l-7.5-4L5 20V4Z" />,
  },
  {
    href: "/progress",
    label: "Progress",
    icon: <path d="M4 19V10M11 19V5M18 19v-7" />,
  },
  {
    href: "/profile",
    label: "Profile",
    icon: (
      <>
        <circle cx="12" cy="8" r="3.4" />
        <path d="M5 20c1.4-4 4-6 7-6s5.6 2 7 6" />
      </>
    ),
  },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="flex border-t border-line bg-paper-raised px-2.5 pt-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))]">
      {NAV_ITEMS.map((item) => {
        const active = pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`relative flex flex-1 flex-col items-center gap-1 pt-1.5 pb-1 ${
              active ? "text-primary" : "text-ink-soft"
            }`}
          >
            {active && (
              <motion.span
                layoutId="nav-active-dot"
                className="absolute -top-2 left-1/2 h-[3px] w-4 -translate-x-1/2 rounded-full bg-gold"
                transition={{ type: "spring", stiffness: 500, damping: 32 }}
              />
            )}
            <motion.svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.8}
              className="h-5 w-5"
              animate={{ scale: active ? 1.1 : 1 }}
              transition={{ type: "spring", stiffness: 400, damping: 15 }}
            >
              {item.icon}
            </motion.svg>
            <span className="text-[10.5px] font-semibold">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
