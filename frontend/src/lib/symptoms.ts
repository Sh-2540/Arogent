/**
 * Mirrors app/ai/synthetic_data.py's SYMPTOM_POOL exactly (same string
 * values) — these are what Arogent Risk's feature vector recognizes.
 * Sending a symptom string not in this list wouldn't error, but it also
 * wouldn't be recognized by the model (app/ai/risk_features.py only
 * checks for these five specific strings), so it's important the two
 * lists never drift apart.
 */
export const SYMPTOM_OPTIONS = [
  { value: "fatigue", label: "Fatigue" },
  { value: "frequent_urination", label: "Frequent urination" },
  { value: "excessive_thirst", label: "Excessive thirst" },
  { value: "blurred_vision", label: "Blurred vision" },
  { value: "slow_healing_wounds", label: "Slow-healing wounds" },
] as const;
