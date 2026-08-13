export type ConfidenceLevel = "low" | "mid" | "high";

export interface QuestionOption {
  letter: "A" | "B" | "C" | "D";
  text: string;
}

export interface Question {
  id: string;
  topic: string;
  topicLabel: string; // e.g. "Passage-based"
  prompt: string;
  passage?: string;
  options: QuestionOption[];
  correctLetter: QuestionOption["letter"];
  explanation: string;
}

export interface OnboardingAnswers {
  name: string;
  targetScore: string | null;
  examTimeline: "1month" | "3months" | "6months" | null; // null => "Flexible"
  dailyStudyTime: "20" | "45" | "60" | null;
  confidence: ConfidenceLevel | null;
}

export const EXAM_TIMELINE_LABELS: Record<string, string> = {
  "1month": "Within 1 month",
  "3months": "2–3 months",
  "6months": "4–6 months",
};

export const STUDY_TIME_LABELS: Record<string, string> = {
  "20": "15–20 min",
  "45": "30–45 min",
  "60": "1 hour+",
};
