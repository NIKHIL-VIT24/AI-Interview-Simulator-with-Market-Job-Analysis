"""
LLaMA Adaptive Interview Engine
- Generates difficulty-adjusted interview questions
- Evaluates answers and gives scores + feedback
- Implements difficulty progression logic
"""
import requests
import json
from config import settings

OLLAMA_URL = f"{settings.OLLAMA_BASE_URL}/api/generate"


def _call_llama(prompt: str) -> str:
    """Send a prompt to LLaMA via Ollama and return the response text."""
    payload = {
        "model": settings.LLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error calling LLaMA: {str(e)}"


def generate_question(
    session_type: str,
    difficulty: int,
    candidate_skills: list,
    previous_questions: list,
    missing_skills: list
) -> str:
    """
    Generate a new adaptive interview question.

    difficulty: 1 (easy) → 4 (very hard)
    """
    difficulty_map = {1: "easy", 2: "medium", 3: "hard", 4: "expert"}
    diff_label = difficulty_map.get(difficulty, "medium")

    skills_str  = ", ".join(candidate_skills) if candidate_skills else "general programming"
    missing_str = ", ".join(missing_skills[:5]) if missing_skills else "none"
    prev_str    = "\n".join(f"- {q}" for q in previous_questions[-3:]) if previous_questions else "none"

    prompt = f"""You are an expert technical interviewer for {session_type} roles.

Candidate skills: {skills_str}
Market-demanded skills candidate is missing: {missing_str}
Recently asked questions (do NOT repeat these):
{prev_str}

Generate ONE {diff_label} interview question (difficulty level {difficulty}/4).
- Focus on real-world application, not just theory.
- If the candidate is missing market skills, subtly probe those areas.
- Return ONLY the question text. No explanation, no numbering.
"""
    return _call_llama(prompt)


def evaluate_answer(question: str, answer: str, difficulty: int) -> dict:
    """
    Evaluate a candidate's answer.
    Returns: score (0-100), feedback, next_difficulty
    """
    prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

Question (difficulty {difficulty}/4):
{question}

Candidate's Answer:
{answer}

Evaluate the answer and respond in this EXACT JSON format (no extra text):
{{
  "score": <integer 0-100>,
  "feedback": "<2-3 sentence constructive feedback>",
  "strengths": "<what they did well>",
  "improvements": "<what they should improve>"
}}
"""
    raw = _call_llama(prompt)

    # Parse JSON safely
    try:
        # Find the JSON block in case LLaMA adds extra text
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        score  = int(result.get("score", 50))
    except Exception:
        score  = 50
        result = {
            "score": score,
            "feedback": raw[:300] if raw else "Could not evaluate answer.",
            "strengths": "",
            "improvements": ""
        }

    # Difficulty Progression Rule (from your architecture doc)
    if score > 85:
        next_difficulty = min(4, difficulty + 1)
    elif score < 50:
        next_difficulty = max(1, difficulty - 1)
    else:
        next_difficulty = difficulty

    result["next_difficulty"] = next_difficulty
    return result


def calculate_technical_score(scores: list, difficulties: list) -> float:
    """
    Weighted Technical Score T = Σ(Si * Di) / Σ(Di)
    (from your architecture doc formula)
    """
    if not scores or not difficulties:
        return 0.0

    weighted_sum = sum(s * d for s, d in zip(scores, difficulties))
    difficulty_sum = sum(difficulties)

    if difficulty_sum == 0:
        return 0.0

    return round(weighted_sum / difficulty_sum, 2)
