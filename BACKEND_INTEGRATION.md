# AceMentor AI — Frontend → Backend Integration Guide

**Audience:** the backend developer wiring FastAPI endpoints into this frontend.
**Status:** frontend is a working Next.js prototype with mock/local data. No real API calls exist yet — this doc maps every screen to the endpoint it needs, using the shapes already defined in `Api_design.txt` and `Database_design.txt` where possible.

---

## 1. Stack & how to run it

```
Next.js 16 (App Router), TypeScript, Tailwind CSS v4
```

```bash
npm install
npm run dev      # localhost:3000
npm run build    # production build (currently passes clean)
```

No environment variables are wired up yet. When you're ready to connect a real API, add:

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

(matches the variable name already specified in `Deployment_architecture.txt`)

---

## 2. Current state: what's real vs. what's a placeholder

**Real:** all UI, all navigation, all component logic, all TypeScript types.

**Placeholder:**
- Onboarding answers save to `localStorage` (`src/lib/studentStore.ts`) instead of `POST /students/profile`
- The question bank is a hardcoded array (`src/lib/questions.ts`) instead of `POST /assessment/start`
- Dashboard, Progress, Coach screens all render **static mock data** written directly in the page components — no fetching happens anywhere yet
- There is no auth. No login/register screens exist. No token is stored or sent. Every route is open.

Everything below tells you exactly where to replace mock data with real fetches.

---

## 3. Route map → backend endpoint mapping

| Frontend route | File | What it needs from the backend |
|---|---|---|
| `/` | `src/app/page.tsx` | None — static splash, auto-navigates to `/onboarding` |
| `/onboarding` | `src/app/onboarding/page.tsx` | On final step: `POST /auth/register` (if this is truly a new user) then `PUT /students/profile` with the collected answers |
| `/assessment` | `src/app/assessment/page.tsx` | `POST /assessment/start` to get questions, `POST /assessment/answer` per answer, `POST /assessment/complete` when done |
| `/diagnosis` | `src/app/diagnosis/page.tsx` | `POST /ai/diagnose` — response renders as the strength/weakness cards |
| `/dashboard` | `src/app/(app)/dashboard/page.tsx` | `GET /progress/dashboard` + `POST /ai/study-plan` (for "Today's mission") |
| `/learning` | `src/app/(app)/learning/page.tsx` | Same dashboard/plan data, filtered down to just the mission summary |
| `/session` | `src/app/session/page.tsx` | `POST /sessions/start` to get the question set, `POST /assessment/answer`-equivalent per question |
| `/session/summary` | `src/app/session/summary/page.tsx` | `POST /sessions/complete` response — accuracy, time, delta vs. last session |
| `/coach` | `src/app/coach/page.tsx` | `POST /ai/coach` for the insight card + each chat turn |
| `/progress` | `src/app/(app)/progress/page.tsx` | `GET /progress/dashboard` + `GET /progress/report` (trend line, radar, mastery bars, weekly stats, streak) |
| `/profile` | `src/app/(app)/profile/page.tsx` | `GET /students/profile` |

---

## 4. Type definitions (already written — match these on the backend)

`src/lib/types.ts`:

```ts
export interface QuestionOption {
  letter: "A" | "B" | "C" | "D";
  text: string;
}

export interface Question {
  id: string;
  topic: string;
  topicLabel: string;       // e.g. "Passage-based"
  prompt: string;
  passage?: string;
  options: QuestionOption[];
  correctLetter: QuestionOption["letter"];
  explanation: string;
}

export interface OnboardingAnswers {
  name: string;
  targetScore: string | null;
  examTimeline: "1month" | "3months" | "6months" | null;  // null = "Flexible"
  dailyStudyTime: "20" | "45" | "60" | null;
  confidence: "low" | "mid" | "high" | null;
}
```

**Action for backend:** `POST /assessment/start` and `POST /sessions/start` should return `Question[]` in exactly this shape — swapping `src/lib/questions.ts`'s static array for a real fetch becomes a one-line change if the shape matches. If your `questions` DB table (per `Database_design.txt`) already stores `question_text`, `answer_options` (JSON), `correct_answer`, and a difficulty/topic field, mapping to this shape server-side is straightforward — just confirm `answer_options` serializes to `{letter, text}[]` rather than a plain string array.

`OnboardingAnswers` should map directly onto `student_profiles` fields (`target_score`, `exam_date`, `study_time_daily`, `confidence_level`) — note `examTimeline` here is a bucketed range, not a date; confirm whether the backend wants a real `exam_date` (in which case the frontend needs a small change to compute one from the bucket) or is fine storing the bucket as-is.

---

## 5. Where to actually wire in `fetch` calls

Nothing currently calls `fetch`. The cleanest integration points, file by file:

- **`src/lib/studentStore.ts`** — currently reads/writes `localStorage`. Replace `saveOnboardingAnswers` with a real `POST`/`PUT` call; keep the function signature the same so `onboarding/page.tsx` doesn't need to change.
- **`src/lib/questions.ts`** — currently exports a static array via `getQuestionSet()`. Turn this into an async function that calls `/assessment/start` or `/sessions/start`, and update the two call sites (`src/app/assessment/page.tsx`, `src/app/session/page.tsx`) to `await` it — both are already client components (`"use client"`), so this just means adding a loading state.
- **Dashboard / Progress / Coach pages** — these are currently server components rendering hardcoded JSX (no `useState`/`useEffect` at all). To fetch real data you'll either need to convert them to client components with `useEffect`, or better, fetch server-side directly in the page component (Next.js App Router supports `async function Page()` with a direct `fetch()` — no client-side loading state needed). I'd recommend the server-side fetch approach for these three screens specifically, since none of them need to be interactive until data has already loaded.

**Recommended, not yet installed:** the original `Frontend_architecture.txt` doc specifies TanStack Query for server state and Zustand for global client state (auth, user info). Neither is installed in this prototype — worth adding once real endpoints exist, especially for the Coach screen's conversational state and any data that needs to refetch/invalidate (e.g. Progress after a session completes).

---

## 6. Auth — not built yet

There is currently:
- No login/register UI
- No token storage (no cookie, no localStorage token)
- No protected-route logic — every screen is publicly reachable by URL

Per `Api_design.txt`, the plan is JWT via `POST /auth/login` → `access_token`. When this gets built, the natural place for a route guard is a new `(app)` layout check (`src/app/(app)/layout.tsx` already exists as the shared shell — this is where a redirect-if-no-token check would go) plus a similar guard on `/session`, `/coach`, `/assessment`, `/diagnosis`, `/session/summary`, which currently sit outside the `(app)` route group and have no shared layout at all.

---

## 7. Known gaps to flag before backend work starts

1. **Only one question exists per topic** in `src/lib/questions.ts` right now — the assessment/session UI is built to handle a full set (progress bar says "Question 1 of 5"/"1 of 3") but only ever shows one question before continuing. This is fine for demo purposes but means the "finish session" / "see my results" transitions are currently hardcoded to fire after a single answer, not a real count.
2. **Session summary is hardcoded to the "good outcome" version.** A low-score variant was designed (amber accent, different copy, "Review with coach" as primary action) but isn't wired into the live route yet — right now `/session/summary` always renders the positive version regardless of actual performance.
3. **No error/loading states exist anywhere.** Every screen assumes data is instantly available. Once real fetches go in, each of these screens will need a loading skeleton and an error state — none of that UI exists yet.

---

## 8. Quick reference: full file tree

```
src/
  app/
    page.tsx                       → splash
    onboarding/page.tsx             → 6-step onboarding
    assessment/page.tsx             → diagnostic assessment (1 question)
    diagnosis/page.tsx              → strengths/weaknesses reveal
    session/page.tsx                → learning session (1 question)
    session/summary/page.tsx        → session summary (good-outcome only)
    coach/page.tsx                  → AI coach chat + insight cards
    (app)/layout.tsx                → shared shell w/ bottom nav
    (app)/dashboard/page.tsx
    (app)/learning/page.tsx
    (app)/progress/page.tsx
    (app)/profile/page.tsx
    globals.css                     → design tokens (colors, fonts, shared classes)
    layout.tsx                      → root layout
  components/
    ui/BottomNav.tsx
    ui/StatRing.tsx
    session/QuestionCard.tsx        → shared question engine (assessment + session)
  lib/
    types.ts                        → shared TS types
    questions.ts                    → mock question bank
    studentStore.ts                 → localStorage placeholder for onboarding data
```

---

Questions on any of this — ping the frontend dev before changing component props/types, since several components (`QuestionCard`, `BottomNav`, `StatRing`) are shared across multiple screens and a shape change in one place affects all of them.
