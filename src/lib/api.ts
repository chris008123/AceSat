"use client";

import { ensureToken, refreshToken } from "./auth";
import { OnboardingAnswers, Question } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  { retryOn401 = true }: { retryOn401?: boolean } = {}
): Promise<T> {
  const token = await ensureToken();

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (res.status === 401 && retryOn401) {
    await refreshToken();
    return request<T>(path, options, { retryOn401: false });
  }

  if (!res.ok) {
    let message = `Request to ${path} failed (${res.status})`;
    try {
      const body = await res.json();
      message = body?.error?.message ?? body?.detail ?? message;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---- Backend response shapes (app/schemas/*) ----

interface BackendQuestionOption {
  letter: string;
  text: string;
}

interface BackendQuestion {
  id: string;
  subject: string;
  topic: string;
  difficulty: number;
  question_text: string;
  options: BackendQuestionOption[];
  correct_answer: string;
  explanation: string | null;
}

interface StartAssessmentResponse {
  assessment_id: string;
  questions: BackendQuestion[];
}

interface SubmitAnswerResponse {
  correct: boolean;
  correct_answer: string;
}

interface CompleteAssessmentResponse {
  status: string;
  message: string;
  score: number;
}

interface StudentProfileResponse {
  target_score: number;
  current_score: number | null;
  exam_date: string | null;
  study_time: number;
  confidence_level: number | null;
  learning_style: string | null;
}

interface DiagnoseResponse {
  weaknesses: string[];
  strengths: string[];
  recommendation: string;
}

interface StudyPlanItem {
  topic: string;
  time: string;
  reason: string;
}

interface StudyPlanResponse {
  plan: StudyPlanItem[];
}

interface CoachResponse {
  explanation: string;
  next_question: string | null;
}

interface StartSessionResponse {
  session_id: string;
  mission: string;
  questions: BackendQuestion[];
}

interface CompleteSessionResponse {
  status: string;
  accuracy: number;
  duration: number;
}

interface DashboardResponse {
  current_score: number | null;
  improvement: string;
  weak_area: string | null;
  streak: number;
}

interface WeeklyReportResponse {
  study_hours: number;
  questions_completed: number;
  recommendation: string;
}

// ---- Mapping helpers ----

/** Converts the backend's question shape into the frontend's `Question`
 * type (src/lib/types.ts), which `QuestionCard` renders. Backend options
 * are already ordered A→D (app/api/routes/assessment.py). */
function toFrontendQuestion(q: BackendQuestion): Question {
  const letters = ["A", "B", "C", "D"] as const;
  return {
    id: q.id,
    topic: q.topic,
    topicLabel: q.topic,
    prompt: q.question_text,
    options: q.options.map((opt) => ({
      letter: (letters.includes(opt.letter as (typeof letters)[number])
        ? opt.letter
        : "A") as Question["options"][number]["letter"],
      text: opt.text,
    })),
    correctLetter: (letters.includes(q.correct_answer as (typeof letters)[number])
      ? q.correct_answer
      : "A") as Question["correctLetter"],
    explanation: q.explanation ?? "No explanation available for this question yet.",
  };
}

function examTimelineToDate(timeline: OnboardingAnswers["examTimeline"]): string | null {
  if (!timeline) return null;
  const months = timeline === "1month" ? 1 : timeline === "3months" ? 3 : 6;
  const d = new Date();
  d.setMonth(d.getMonth() + months);
  return d.toISOString().slice(0, 10);
}

function confidenceToLevel(confidence: OnboardingAnswers["confidence"]): number | null {
  if (confidence === "low") return 1;
  if (confidence === "mid") return 3;
  if (confidence === "high") return 5;
  return null;
}

// ---- Public API ----

export const api = {
  async createProfile(answers: OnboardingAnswers): Promise<StudentProfileResponse> {
    return request<StudentProfileResponse>("/students/profile", {
      method: "POST",
      body: JSON.stringify({
        target_score: answers.targetScore ? parseInt(answers.targetScore, 10) : undefined,
        exam_date: examTimelineToDate(answers.examTimeline),
        study_time: answers.dailyStudyTime ? parseInt(answers.dailyStudyTime, 10) : undefined,
        confidence_level: confidenceToLevel(answers.confidence),
      }),
    });
  },

  async getProfile(): Promise<StudentProfileResponse> {
    return request<StudentProfileResponse>("/students/profile");
  },

  async startAssessment(): Promise<{ assessmentId: string; questions: Question[] }> {
    const res = await request<StartAssessmentResponse>("/assessment/start", { method: "POST" });
    return { assessmentId: res.assessment_id, questions: res.questions.map(toFrontendQuestion) };
  },

  async submitAssessmentAnswer(
    assessmentId: string,
    questionId: string,
    answerLetter: string,
    timeTakenSeconds: number,
    confidence = 3
  ): Promise<SubmitAnswerResponse> {
    return request<SubmitAnswerResponse>(`/assessment/answer?assessment_id=${assessmentId}`, {
      method: "POST",
      body: JSON.stringify({
        question_id: questionId,
        answer: answerLetter,
        confidence,
        time_taken: timeTakenSeconds,
      }),
    });
  },

  async completeAssessment(assessmentId: string): Promise<CompleteAssessmentResponse> {
    return request<CompleteAssessmentResponse>(`/assessment/complete?assessment_id=${assessmentId}`, {
      method: "POST",
    });
  },

  async diagnose(): Promise<DiagnoseResponse> {
    return request<DiagnoseResponse>("/ai/diagnose", { method: "POST" });
  },

  async studyPlan(): Promise<StudyPlanResponse> {
    return request<StudyPlanResponse>("/ai/study-plan", { method: "POST" });
  },

  async coach(question: string): Promise<CoachResponse> {
    return request<CoachResponse>("/ai/coach", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },

  async startSession(): Promise<{ sessionId: string; mission: string; questions: Question[] }> {
    const res = await request<StartSessionResponse>("/sessions/start", { method: "POST" });
    return { sessionId: res.session_id, mission: res.mission, questions: res.questions.map(toFrontendQuestion) };
  },

  async completeSession(
    sessionId: string,
    accuracy: number,
    durationSeconds: number
  ): Promise<CompleteSessionResponse> {
    return request<CompleteSessionResponse>(`/sessions/complete?session_id=${sessionId}`, {
      method: "POST",
      body: JSON.stringify({ accuracy, duration: durationSeconds }),
    });
  },

  async getDashboard(): Promise<DashboardResponse> {
    return request<DashboardResponse>("/progress/dashboard");
  },

  async getReport(): Promise<WeeklyReportResponse> {
    return request<WeeklyReportResponse>("/progress/report");
  },
};

export type {
  DashboardResponse,
  DiagnoseResponse,
  StudentProfileResponse,
  StudyPlanItem,
  StudyPlanResponse,
  WeeklyReportResponse,
};
