"use client";

/**
 * Onboarding answers now get persisted for real via `api.createProfile`
 * (POST /students/profile) rather than localStorage. The one exception
 * is `name` — the backend's `student_profiles` table has no name column
 * (Api_design.txt §6 / Database_design.txt), so there's nowhere to store
 * it remotely. It's kept here purely for local greeting text (e.g.
 * "Good morning, Sarah" on the dashboard).
 */

const NAME_KEY = "acementor:name";

export function saveLocalName(name: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(NAME_KEY, name);
}

export function getLocalName(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(NAME_KEY);
}
