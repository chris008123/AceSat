export default function ProfilePage() {
  return (
    <div className="flex flex-col gap-4 px-4.5 py-5">
      <div className="flex flex-col items-center pt-3.5 pb-1 text-center">
        <div className="font-display mb-2.5 flex h-16 w-16 items-center justify-center rounded-full bg-ink text-[22px] font-semibold text-white">
          S
        </div>
        <h2 className="font-display text-[17px]">Sarah</h2>
        <p className="mt-0.5 text-[12px] text-ink-soft">Target score 1400 · 7-day streak</p>
      </div>

      <div className="card">
        {[
          { k: "Exam date", v: "Nov 2026" },
          { k: "Daily goal", v: "30–45 min" },
          { k: "Member since", v: "6 weeks ago" },
          { k: "Notifications", v: "On" },
        ].map((row, i, arr) => (
          <div
            key={row.k}
            className={`flex items-center justify-between py-3 text-[13px] ${
              i < arr.length - 1 ? "border-b border-line" : ""
            }`}
          >
            <span className="text-ink-soft">{row.k}</span>
            <span className="font-mono text-[12.5px] font-semibold">{row.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
