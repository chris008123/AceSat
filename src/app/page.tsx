"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getLocalName } from "@/lib/studentStore";

/**
 * Static splash — per BACKEND_INTEGRATION.md §3, this route has nothing
 * to fetch. It just decides where to send the visitor: straight into the
 * dashboard if this device has already finished onboarding (we have a
 * locally-remembered name), otherwise into onboarding.
 *
 * (This file previously contained a stray copy of `/session`'s page —
 * fixed as part of the backend integration pass.)
 */
export default function SplashPage() {
  const router = useRouter();

  useEffect(() => {
    const hasOnboarded = !!getLocalName();
    router.replace(hasOnboarded ? "/dashboard" : "/onboarding");
  }, [router]);

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col items-center justify-center bg-paper">
      <div className="flex h-16 w-16 items-center justify-center rounded-[18px] bg-ink">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2} className="h-7 w-7">
          <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
        </svg>
      </div>
    </div>
  );
}
