"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import BottomNav from "@/components/ui/BottomNav";
import { getLocalName } from "@/lib/studentStore";

const noopSubscribe = () => () => {};

/** localStorage isn't available during the static/server render, so
 * this needs to come from an external store rather than plain state —
 * keeps the guard below from having to call setState inside an effect
 * just to sync a value that already lives outside React. */
function useLocalName(): string | null {
  return useSyncExternalStore(noopSubscribe, getLocalName, () => null);
}

/**
 * Route guard, added per BACKEND_INTEGRATION.md §6: since there's still
 * no login UI, "authenticated" here just means "this device has
 * finished onboarding" (i.e. `getLocalName()` has a value — the API
 * client bootstraps the actual anonymous account/token separately, see
 * src/lib/auth.ts). Good enough to stop someone bookmarking
 * `/dashboard` before ever onboarding; not a real auth boundary.
 */
export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const name = useLocalName();

  useEffect(() => {
    if (name === null) {
      router.replace("/onboarding");
    }
  }, [name, router]);

  if (name === null) return null;

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex-1 overflow-y-auto">{children}</div>
      <BottomNav />
    </div>
  );
}
