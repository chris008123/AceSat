"use client";

import { useEffect, useState } from "react";
import { api, StudentProfileResponse } from "@/lib/api";
import { getLocalName } from "@/lib/studentStore";

export default function ProfilePage() {
  const [profile, setProfile] = useState<StudentProfileResponse | null>(null);
  const name = getLocalName() ?? "Student";

  useEffect(() => {
    api.getProfile().then(setProfile).catch(() => setProfile(null));
  }, []);

  const examDate = profile?.exam_date
    ? new Date(profile.exam_date).toLocaleDateString(undefined, { month: "short", year: "numeric" })
    : "Not set";

  return (
    <div className="flex flex-col gap-4 px-4.5 py-5">
      <div className="flex flex-col items-center pt-3.5 pb-1 text-center">
        <div className="font-display mb-2.5 flex h-16 w-16 items-center justify-center rounded-full bg-ink text-[22px] font-semibold text-white">
          {name[0]?.toUpperCase() ?? "S"}
        </div>
        <h2 className="font-display text-[17px]">{name}</h2>
        <p className="mt-0.5 text-[12px] text-ink-soft">
          {profile ? `Target score ${profile.target_score}` : "Loading…"}
        </p>
      </div>

      <div className="card">
        {[
          { k: "Exam date", v: examDate },
          { k: "Daily goal", v: profile ? `${profile.study_time} min` : "—" },
          { k: "Current estimate", v: profile?.current_score ? String(profile.current_score) : "Not yet estimated" },
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
