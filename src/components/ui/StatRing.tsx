"use client";

interface StatRingProps {
  percent: number; // 0-100
  label: string;
  color?: string; // css var, defaults to primary
  size?: number;
}

export default function StatRing({
  percent,
  label,
  color = "var(--primary)",
  size = 140,
}: StatRingProps) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div
      className="relative"
      style={{ width: size, height: size }}
    >
      <svg
        viewBox="0 0 140 140"
        style={{ width: size, height: size, transform: "rotate(-90deg)" }}
      >
        <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--line)" strokeWidth={10} />
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          style={{
            animation: `stat-ring-in 1.1s cubic-bezier(.4,0,.2,1) .3s forwards`,
            // @ts-expect-error -- custom property for the keyframe below
            "--ring-offset": offset,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="font-mono text-[28px] font-medium leading-none">{percent}%</div>
        <div className="mt-1 text-[10.5px] text-ink-soft">{label}</div>
      </div>
      <style jsx>{`
        @keyframes stat-ring-in {
          to {
            stroke-dashoffset: var(--ring-offset);
          }
        }
      `}</style>
    </div>
  );
}
