"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

export default function CoachPage() {
  const router = useRouter();
  const feedRef = useRef<HTMLDivElement>(null);
  const [studentMsg, setStudentMsg] = useState<string | null>(null);
  const [typing, setTyping] = useState(false);
  const [replied, setReplied] = useState(false);
  const [input, setInput] = useState("");
  const sentRef = useRef(false);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  function sendMessage(text: string) {
    if (sentRef.current || !text.trim()) return;
    sentRef.current = true;
    setStudentMsg(text);
    scrollToBottom();

    setTimeout(() => {
      setTyping(true);
      scrollToBottom();
    }, 350);

    setTimeout(() => {
      setTyping(false);
      setReplied(true);
      scrollToBottom();
    }, 1500);
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex items-center gap-2.5 border-b border-line bg-paper-raised px-4.5 pt-4.5 pb-3.5">
        <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-[11px] bg-ink">
          <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2} className="h-[17px] w-[17px]">
            <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
          </svg>
          <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-paper-raised bg-primary" />
        </div>
        <div className="leading-tight">
          <h1 className="font-display text-[15px] font-semibold">Your Coach</h1>
          <p className="text-[11px] text-ink-soft">Reviewing today&apos;s session</p>
        </div>
        <button
          onClick={() => router.push("/dashboard")}
          className="ml-auto flex h-[30px] w-[30px] items-center justify-center rounded-full border border-line bg-paper text-ink-soft"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3.5 w-3.5">
            <path d="M15 6l-6 6 6 6" />
          </svg>
        </button>
      </div>

      <div ref={feedRef} className="flex flex-1 flex-col gap-3.5 overflow-y-auto px-4 pb-2.5 pt-4.5">
        {/* insight card — leads the feed, not a greeting bubble */}
        <div className="rounded-[14px] border border-line border-l-[3px] border-l-primary bg-paper-raised p-3.5 shadow-sm">
          <div className="mb-2 flex items-center gap-1.5 text-[10.5px] font-semibold uppercase tracking-wide text-primary-deep">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-3 w-3">
              <path d="M12 20V10M18 20V4M6 20v-6" />
            </svg>
            Pattern noticed
          </div>
          <p className="text-[13px] leading-relaxed text-ink">
            You&apos;ve missed <b className="font-semibold">3 of the last 4</b> inference questions
            where the evidence was a physical action rather than dialogue. That&apos;s a specific,
            fixable pattern.
          </p>
          <div className="mt-3 flex gap-2">
            <span className="cursor-pointer rounded-full bg-primary px-3.5 py-2 text-[12px] font-semibold text-white">
              Practice this →
            </span>
            <span className="cursor-pointer rounded-full border border-line bg-paper px-3.5 py-2 text-[12px] font-semibold text-ink">
              Remind me later
            </span>
          </div>
        </div>

        {/* recommendation card */}
        <div className="rounded-[14px] border border-line bg-paper-raised p-3.5 shadow-sm">
          <div className="mb-1.5 flex items-start justify-between gap-2.5">
            <h3 className="font-display text-[14.5px] font-semibold">Adjusted tomorrow&apos;s plan</h3>
            <span className="whitespace-nowrap rounded-full bg-gold-dim px-2 py-0.5 font-mono text-[11px] text-gold">
              +10 min
            </span>
          </div>
          <p className="mb-2.5 text-[12.5px] leading-relaxed text-ink-soft">
            I added a short inference drill focused on action-based evidence, and trimmed vocabulary
            time since you&apos;re already at 91% there.
          </p>
          <button className="rounded-full bg-primary-dim px-3.5 py-2 text-[12.5px] font-semibold text-primary-deep">
            View plan
          </button>
        </div>

        <CoachBubble>
          Want to walk through one of those missed questions together right now, or later during
          your session?
        </CoachBubble>

        {studentMsg && (
          <div className="ml-auto max-w-[78%] rounded-[14px] rounded-tr-[3px] bg-ink px-3.5 py-2.5 text-[13px] leading-relaxed text-white">
            {studentMsg}
          </div>
        )}

        {typing && (
          <div className="flex max-w-[88%] gap-2.5">
            <CoachAvatar />
            <div className="flex items-center gap-1 rounded-[14px] rounded-tl-[3px] border border-line bg-paper-raised px-4 py-3.5">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-soft"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
          </div>
        )}

        {replied && (
          <CoachBubble>
            Good — let&apos;s do it now while it&apos;s fresh. I&apos;ll pull up the passage from
            question 6. Look for what the character <i>does</i>, not just what they say. Ready?
          </CoachBubble>
        )}
      </div>

      <div className="border-t border-line bg-paper-raised px-3.5 pt-3 pb-[calc(0.9rem+env(safe-area-inset-bottom))]">
        <div className="mb-2.5 flex gap-2 overflow-x-auto pb-0.5">
          {["Let's do it now", "Remind me tonight", "Why does this matter?"].map((chip) => (
            <button
              key={chip}
              onClick={() => sendMessage(chip)}
              className="shrink-0 whitespace-nowrap rounded-full bg-primary-dim px-3.5 py-2 text-[12px] font-medium text-primary-deep"
            >
              {chip}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 rounded-full border border-line bg-paper py-1 pl-4 pr-1">
          <input
            type="text"
            placeholder="Ask your coach anything…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage(input);
            }}
            className="flex-1 bg-transparent text-[13.5px] text-ink outline-none"
          />
          <button
            onClick={() => sendMessage(input)}
            className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full bg-primary text-white"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} className="h-[15px] w-[15px]">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

function CoachAvatar() {
  return (
    <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-[7px] bg-ink">
      <svg viewBox="0 0 24 24" fill="none" stroke="var(--gold)" strokeWidth={2} className="h-[11px] w-[11px]">
        <path d="M12 3l2.6 5.6L21 9.3l-4.5 4.1L17.6 20 12 16.8 6.4 20l1.1-6.6L3 9.3l6.4-.7z" />
      </svg>
    </div>
  );
}

function CoachBubble({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex max-w-[88%] gap-2.5">
      <CoachAvatar />
      <div className="rounded-[14px] rounded-tl-[3px] border border-line bg-paper-raised px-3.5 py-2.5 text-[13px] leading-relaxed text-ink">
        {children}
      </div>
    </div>
  );
}
