import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-4 px-4.5 py-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-[19px] font-semibold">Good morning, Sarah</h1>
          <p className="mt-0.5 text-[12.5px] text-ink-soft">
            Reading is your biggest opportunity today
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1.5 rounded-full bg-gold-dim px-3 py-1.5 font-mono text-[12px] font-medium text-[#8A5A12]">
          🔥 7 days
        </div>
      </div>

      <Link href="/session" className="card flex flex-col gap-3">
        <div className="eyebrow">Today&apos;s mission</div>
        <div className="flex items-start justify-between gap-2.5">
          <div>
            <h2 className="font-display text-[17px] font-semibold">
              Reading Inference Practice
            </h2>
            <p className="mt-1 text-[12.5px] text-ink-soft">
              Chosen because your last 3 sessions dropped in accuracy
            </p>
          </div>
          <div className="font-mono text-[12px] whitespace-nowrap text-ink-soft">20 min</div>
        </div>
        <span className="btn-primary text-center">Start session</span>
      </Link>

      <div className="grid grid-cols-2 gap-3.5">
        <div className="card">
          <div className="eyebrow mb-2.5">Progress</div>
          <div className="flex flex-col gap-2.5">
            {[
              { label: "Math", pct: 72, color: "var(--primary)" },
              { label: "Reading", pct: 55, color: "var(--gold)" },
              { label: "Writing", pct: 65, color: "var(--primary)" },
            ].map((row) => (
              <div key={row.label} className="flex items-center gap-2.5">
                <span className="w-[52px] shrink-0 text-[12px] text-ink-soft">{row.label}</span>
                <div className="h-[7px] flex-1 overflow-hidden rounded-full bg-line">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${row.pct}%`, background: row.color }}
                  />
                </div>
                <span className="w-8 text-right font-mono text-[11.5px] text-ink-soft">
                  {row.pct}%
                </span>
              </div>
            ))}
          </div>
        </div>

        <Link href="/coach" className="card">
          <div className="eyebrow mb-2.5">Coach note</div>
          <p className="mb-3 text-[13px] leading-relaxed text-ink">
            You&apos;re guessing correctly on <b>inference questions</b> without spotting the
            evidence. Let&apos;s fix that pattern.
          </p>
          <span className="inline-flex items-center gap-1 text-[12.5px] font-semibold text-primary-deep">
            Review with Coach →
          </span>
        </Link>
      </div>
    </div>
  );
}
