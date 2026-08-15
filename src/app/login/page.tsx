"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginWithCredentials } from "@/lib/auth";
import { getLocalName } from "@/lib/studentStore";
import CoachMark from "@/components/ui/CoachMark";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = email.trim().length > 0 && password.length > 0 && !submitting;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      await loginWithCredentials(email, password);
      // Existing accounts that already finished onboarding (i.e. we
      // have a locally-remembered name) skip straight to the dashboard;
      // otherwise treat this like a fresh account and collect the
      // onboarding answers before letting them in.
      router.push(getLocalName() ? "/dashboard" : "/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't log in — try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      <div className="flex flex-1 flex-col overflow-y-auto px-6 pb-5 pt-10">
        <div className="mb-7 flex flex-col items-center text-center">
          <CoachMark size={56} animated={false} />
          <h1 className="font-display mt-4 text-[22px] font-semibold">Welcome back</h1>
          <p className="mt-1.5 max-w-[280px] text-[13px] leading-relaxed text-ink-soft">
            Log in to pick up right where you left off.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-[12px] font-semibold text-ink-soft">Email</label>
            <input
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-[14px] border-[1.5px] border-line bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[12px] font-semibold text-ink-soft">Password</label>
            <input
              type="password"
              autoComplete="current-password"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="rounded-[14px] border-[1.5px] border-line bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary"
            />
          </div>

          {error && <p className="text-center text-[12px] text-warm-deep">{error}</p>}

          <div className="mt-auto flex flex-col gap-3 pt-2">
            <button type="submit" className="btn-primary" disabled={!canSubmit}>
              {submitting ? "Logging in…" : "Log in"}
            </button>
            <p className="text-center text-[12.5px] text-ink-soft">
              New here?{" "}
              <Link href="/register" className="font-semibold text-primary-deep">
                Create an account
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
