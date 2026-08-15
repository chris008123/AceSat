interface SkeletonLineProps {
  width?: string;
  height?: number;
  className?: string;
}

export function SkeletonLine({ width = "100%", height = 12, className = "" }: SkeletonLineProps) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ width, height, borderRadius: 6 }}
    />
  );
}

/** Mirrors the shape of the mission/coach-note cards on the dashboard —
 * swap in while `useEffect` data hasn't resolved yet. */
export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="card flex flex-col gap-2.5">
      <SkeletonLine width="40%" height={10} />
      <SkeletonLine width="70%" height={16} />
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLine key={i} width={i === lines - 1 ? "55%" : "90%"} />
      ))}
    </div>
  );
}

export function SkeletonRing({ size = 140 }: { size?: number }) {
  return (
    <div
      className="skeleton rounded-full"
      style={{ width: size, height: size, borderRadius: "9999px" }}
    />
  );
}
