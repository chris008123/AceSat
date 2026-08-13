import { Question } from "./types";

export const readingInferenceQuestions: Question[] = [
  {
    id: "q1",
    topic: "reading-inference",
    topicLabel: "Passage-based",
    prompt:
      "Which choice best supports the idea that the narrator initially distrusts the visitor?",
    passage:
      "\u201c...she watched him from the doorway a long moment before speaking, her hand still resting on the latch as if she might yet close it.\u201d",
    options: [
      { letter: "A", text: "She watched him from the doorway." },
      { letter: "B", text: "Her hand stayed on the latch, ready to close it." },
      { letter: "C", text: "She waited a long moment before speaking." },
      { letter: "D", text: "He stood outside until she noticed him." },
    ],
    correctLetter: "B",
    explanation:
      "The physical detail — her hand staying on the latch — is an action that reveals she's ready to shut him out. That's stronger evidence than description alone.",
  },
  {
    id: "q2",
    topic: "reading-inference",
    topicLabel: "Passage-based",
    prompt: "What does the visitor's prolonged silence most strongly suggest?",
    passage:
      "\u201cHe said nothing, only turned the brim of his hat slowly between his fingers, and looked past her toward the fields.\u201d",
    options: [
      { letter: "A", text: "He is admiring the scenery." },
      { letter: "B", text: "He is avoiding eye contact out of discomfort." },
      { letter: "C", text: "He has forgotten why he came." },
      { letter: "D", text: "He is waiting for her to speak first." },
    ],
    correctLetter: "B",
    explanation:
      "Turning his hat and looking away are both physical signs of unease — the passage is showing discomfort through action, not stating it directly.",
  },
];

export const algebraQuestions: Question[] = [
  {
    id: "q3",
    topic: "algebra-word-problems",
    topicLabel: "Word problem",
    prompt:
      "A rectangular garden has a perimeter of 60 feet. If the length is twice the width, what is the width?",
    options: [
      { letter: "A", text: "8 feet" },
      { letter: "B", text: "10 feet" },
      { letter: "C", text: "12 feet" },
      { letter: "D", text: "15 feet" },
    ],
    correctLetter: "B",
    explanation:
      "Setting up 2(w + 2w) = 60 gives 6w = 60, so w = 10. The setup — translating the sentence into an equation — is the real skill being tested here.",
  },
];

export function getQuestionSet(topic: "reading" | "algebra" | "diagnostic"): Question[] {
  if (topic === "algebra") return algebraQuestions;
  if (topic === "diagnostic") return [readingInferenceQuestions[0]];
  return readingInferenceQuestions;
}
