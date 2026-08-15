"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import CoachMark from "@/components/ui/CoachMark";

interface ChatTurn {
  from: "student" | "coach";
  text: string;
}

export default function CoachPage() {
  const router = useRouter();
  const feedRef = useRef<HTMLDivElement>(null);
  const [insight, setInsight] = useState<string | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [typing, setTyping] = useState(false);
  const [input, setInput] = useState("");
  const sendingRef = useRef(false);

  useEffect(() => {
    api
      .diagnose()
      .then((d) => {
        if (d.weaknesses.length > 0) {
          setInsight(
            `Your current focus area is ${d.weaknesses[0]}. ${d.recommendation}`
          );
        } else {
          setInsight(d.recommendation);
        }
      })
      .catch(() =>
        setInsight("Complete a session or two and I'll start noticing patterns worth flagging.")
      );
  }, []);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  async function sendMessage(text: string) {
    if (sendingRef.current || !text.trim()) return;
    sendingRef.current = true;
    setInput("");
    setTurns((prev) => [...prev, { from: "student", text }]);
    setTyping(true);
    scrollToBottom();

    try {
      const res = await api.coach(text);
      const reply = res.next_question ? `${res.explanation} ${res.next_question}` : res.explanation;
      setTurns((prev) => [...prev, { from: "coach", text: reply }]);
    } catch {
      setTurns((prev) => [
        ...prev,
        { from: "coach", text: "I couldn't reach the server just now — try again in a moment." },
      ]);
    } finally {
      setTyping(false);
      sendingRef.current = false;
      scrollToBottom();
    }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper page-enter">
      <div className="flex items-center gap-2.5 border-b border-line bg-paper-raised px-4.5 pt-4.5 pb-3.5">
        <CoachMark size={40} showPulse />
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
            {insight ?? "Looking at your recent answers…"}
          </p>
        </div>

        {turns.map((t, i) =>
          t.from === "student" ? (
            <div
              key={i}
              className="ml-auto max-w-[78%] rounded-[14px] rounded-tr-[3px] bg-ink px-3.5 py-2.5 text-[13px] leading-relaxed text-white"
            >
              {t.text}
            </div>
          ) : (
            <CoachBubble key={i}>{t.text}</CoachBubble>
          )
        )}

        {typing && <ThinkingBubble />}
      </div>

      <div className="border-t border-line bg-paper-raised px-3.5 pt-3 pb-[calc(0.9rem+env(safe-area-inset-bottom))]">
        <div className="mb-2.5 flex gap-2 overflow-x-auto pb-0.5">
          {["What should I practice next?", "Why does this matter?", "Give me an example"].map((chip) => (
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
  return <CoachMark size={24} animated={false} className="mt-0.5 shrink-0" />;
}

const THINKING_PHRASES = [
  "Reviewing your last session…",
  "Checking for patterns…",
  "Comparing against your goal…",
];

/** Cycles short reasoning phrases instead of a generic "…" indicator —
 * reinforces that the coach is doing agent-style analysis, not just
 * generating text (see Prompt_strategy.txt / "not a chatbot" framing). */
function ThinkingBubble() {
  const [phraseIndex, setPhraseIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setPhraseIndex((i) => (i + 1) % THINKING_PHRASES.length);
    }, 900);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex max-w-[88%] gap-2.5">
      <CoachMark size={24} className="mt-0.5 shrink-0" />
      <div className="flex items-center gap-2 rounded-[14px] rounded-tl-[3px] border border-line bg-paper-raised px-4 py-3.5">
        <span className="text-[12.5px] text-ink-soft transition-opacity duration-200">
          {THINKING_PHRASES[phraseIndex]}
        </span>
        <span className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </span>
      </div>
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
