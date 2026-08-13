const DAYS = ["M", "T", "W", "T", "F", "S", "S"];
const DONE_COUNT = 6; // first 6 days complete, 7th is "today"

export default function ProgressPage() {
  return (
    <div className="flex flex-col gap-4 px-4.5 py-5">
      <div>
        <h1 className="font-display text-[19px] font-semibold">Your Progress</h1>
        <p className="mt-0.5 text-[12px] text-ink-soft">Since you started · 6 weeks ago</p>
      </div>

      {/* score trend */}
      <div className="card">
        <div className="eyebrow mb-2.5 flex w-full items-center justify-between normal-case tracking-normal">
          <span className="uppercase tracking-wide">Estimated SAT score</span>
          <span className="pill-mono">1200 · +150</span>
        </div>
        <svg viewBox="0 0 320 110" preserveAspectRatio="none" className="block h-[110px] w-full">
          <line x1="0" y1="27" x2="320" y2="27" stroke="#E4E7F0" strokeWidth="1" />
          <line x1="0" y1="55" x2="320" y2="55" stroke="#E4E7F0" strokeWidth="1" />
          <line x1="0" y1="83" x2="320" y2="83" stroke="#E4E7F0" strokeWidth="1" />
          <path
            d="M0,95 L64,88 L128,70 L192,58 L256,40 L320,15"
            fill="none"
            stroke="#1E9E64"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M0,95 L64,88 L128,70 L192,58 L256,40 L320,15 L320,110 L0,110 Z"
            fill="url(#trendGradient)"
            opacity="0.5"
          />
          <defs>
            <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1E9E64" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#1E9E64" stopOpacity="0" />
            </linearGradient>
          </defs>
          <circle cx="320" cy="15" r="4.5" fill="#1E9E64" />
        </svg>
        <div className="mt-1.5 flex justify-between">
          {["WK1", "WK2", "WK3", "WK4", "WK5", "NOW"].map((l) => (
            <span key={l} className="font-mono text-[10px] text-ink-soft">
              {l}
            </span>
          ))}
        </div>
      </div>

      {/* skill radar */}
      <div className="card">
        <div className="eyebrow mb-2.5">Skill balance</div>
        <div className="flex justify-center">
          <svg viewBox="0 0 220 220" className="h-[210px] w-[210px]">
            <polygon points="110,30 176,75 152,155 68,155 44,75" fill="none" stroke="#E4E7F0" strokeWidth="1" />
            <polygon points="110,50 158,85 140,140 80,140 62,85" fill="none" stroke="#E4E7F0" strokeWidth="1" />
            <polygon points="110,70 140,95 128,125 92,125 80,95" fill="none" stroke="#E4E7F0" strokeWidth="1" />
            <line x1="110" y1="110" x2="110" y2="30" stroke="#E4E7F0" strokeWidth="1" />
            <line x1="110" y1="110" x2="176" y2="75" stroke="#E4E7F0" strokeWidth="1" />
            <line x1="110" y1="110" x2="152" y2="155" stroke="#E4E7F0" strokeWidth="1" />
            <line x1="110" y1="110" x2="68" y2="155" stroke="#E4E7F0" strokeWidth="1" />
            <line x1="110" y1="110" x2="44" y2="75" stroke="#E4E7F0" strokeWidth="1" />
            <polygon
              points="110,52 163,88 130,133 84,132 74,90"
              fill="#1E9E64"
              fillOpacity="0.18"
              stroke="#1E9E64"
              strokeWidth="2.2"
              strokeLinejoin="round"
            />
            {[
              [110, 52],
              [163, 88],
              [130, 133],
              [84, 132],
              [74, 90],
            ].map(([cx, cy]) => (
              <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="3.5" fill="#1E9E64" />
            ))}
            <text x="110" y="20" textAnchor="middle" fontSize="10" fill="#5B6580">Math</text>
            <text x="192" y="72" textAnchor="start" fontSize="10" fill="#5B6580">Vocab</text>
            <text x="163" y="172" textAnchor="middle" fontSize="10" fill="#5B6580">Grammar</text>
            <text x="57" y="172" textAnchor="middle" fontSize="10" fill="#5B6580">Reading</text>
            <text x="28" y="72" textAnchor="end" fontSize="10" fill="#5B6580">Prob. Solve</text>
          </svg>
        </div>
      </div>

      {/* mastery bars */}
      <div className="card">
        <div className="eyebrow mb-2.5">Topic mastery</div>
        <div className="flex flex-col gap-2.5">
          {[
            { label: "Vocabulary", pct: 91, color: "var(--primary)" },
            { label: "Math", pct: 72, color: "var(--primary)" },
            { label: "Grammar", pct: 65, color: "var(--gold)" },
            { label: "Reading", pct: 55, color: "var(--gold)" },
          ].map((row) => (
            <div key={row.label} className="flex items-center gap-2.5">
              <span className="w-[72px] shrink-0 text-[12px] text-ink">{row.label}</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-line">
                <div className="h-full rounded-full" style={{ width: `${row.pct}%`, background: row.color }} />
              </div>
              <span className="w-8 text-right font-mono text-[11.5px] text-ink-soft">{row.pct}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* weekly report */}
      <div className="card">
        <div className="eyebrow mb-2.5">This week</div>
        <div className="grid grid-cols-2 gap-2.5">
          {[
            { v: "4h 20m", l: "Study time" },
            { v: "186", l: "Questions done" },
            { v: "76%", l: "Avg accuracy" },
            { v: "6/7", l: "Days active" },
          ].map((s) => (
            <div key={s.l} className="rounded-[9px] bg-paper px-3 py-2.5">
              <div className="font-mono text-[16px] font-medium">{s.v}</div>
              <div className="mt-0.5 text-[10.5px] text-ink-soft">{s.l}</div>
            </div>
          ))}
        </div>
      </div>

      {/* streak */}
      <div className="card">
        <div className="eyebrow mb-2.5 flex w-full items-center justify-between normal-case tracking-normal">
          <span className="uppercase tracking-wide">Learning streak</span>
          <span className="pill-mono">🔥 7 days</span>
        </div>
        <div className="flex justify-between gap-1.5">
          {DAYS.map((d, i) => {
            const done = i < DONE_COUNT;
            const today = i === DONE_COUNT;
            return (
              <div key={i} className="flex flex-1 flex-col items-center gap-1.5">
                <span className="text-[10px] text-ink-soft">{d}</span>
                <div
                  className={`flex h-[26px] w-[26px] items-center justify-center rounded-lg ${
                    done ? "bg-primary" : today ? "border-2 border-gold bg-paper-raised" : "bg-line"
                  }`}
                >
                  {done && (
                    <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={3} className="h-3 w-3">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
