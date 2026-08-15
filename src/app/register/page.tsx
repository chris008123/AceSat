"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { registerWithCredentials } from "@/lib/auth";
import CoachMark from "@/components/ui/CoachMark";

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emailValid = email.length === 0 || isValidEmail(email);
  const passwordValid = password.length === 0 || password.length >= 8;
  const passwordsMatch = confirmPassword.length === 0 || confirmPassword === password;

  const canSubmit =
    isValidEmail(email) && password.length >= 8 && confirmPassword === password && !submitting;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      await registerWithCredentials(email, password);
      router.push("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't create your account — try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      <div className="flex flex-1 flex-col overflow-y-auto px-6 pb-5 pt-10">
        <div className="mb-7 flex flex-col items-center text-center">
          <CoachMark size={56} animated={false} />
          <h1 className="font-display mt-4 text-[22px] font-semibold">Create your account</h1>
          <p className="mt-1.5 max-w-[280px] text-[13px] leading-relaxed text-ink-soft">
            So your progress follows you — even if you switch devices.
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
              className={`rounded-[14px] border-[1.5px] bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary ${
                emailValid ? "border-line" : "border-warm"
              }`}
            />
            {!emailValid && <p className="text-[11.5px] text-warm-deep">Enter a valid email address.</p>}
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[12px] font-semibold text-ink-soft">Password</label>
            <input
              type="password"
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`rounded-[14px] border-[1.5px] bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary ${
                passwordValid ? "border-line" : "border-warm"
              }`}
            />
            {!passwordValid && <p className="text-[11.5px] text-warm-deep">Password needs at least 8 characters.</p>}
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[12px] font-semibold text-ink-soft">Confirm password</label>
            <input
              type="password"
              autoComplete="new-password"
              placeholder="Type it again"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={`rounded-[14px] border-[1.5px] bg-paper-raised px-4 py-3.5 text-[15px] text-ink outline-none focus:border-primary ${
                passwordsMatch ? "border-line" : "border-warm"
              }`}
            />
            {!passwordsMatch && <p className="text-[11.5px] text-warm-deep">Passwords don&apos;t match.</p>}
          </div>

          {error && <p className="text-center text-[12px] text-warm-deep">{error}</p>}

          <div className="mt-auto flex flex-col gap-3 pt-2">
            <button type="submit" className="btn-primary" disabled={!canSubmit}>
              {submitting ? "Creating account…" : "Create account"}
            </button>
            <p className="text-center text-[12.5px] text-ink-soft">
              Already have an account?{" "}
              <Link href="/login" className="font-semibold text-primary-deep">
                Log in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
