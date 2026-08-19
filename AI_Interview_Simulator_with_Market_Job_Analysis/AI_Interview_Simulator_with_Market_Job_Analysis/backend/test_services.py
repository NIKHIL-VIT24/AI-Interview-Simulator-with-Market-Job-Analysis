"""
Backend Unit Tests
Tests all core logic WITHOUT needing GPU, API keys, or PostgreSQL.
Run with: python test_services.py

Tests:
  - Behavioral score formula
  - Resume scoring logic
  - Hiring probability prediction
  - Difficulty progression rule
  - GPU memory manager
  - Resume text parsing utilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ── Color output helpers ──────────────────────────────────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

passed = 0
failed = 0

def test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        print(f"  {GREEN}✓ PASS{RESET} — {name}")
        passed += 1
    else:
        print(f"  {RED}✗ FAIL{RESET} — {name}" + (f" | {detail}" if detail else ""))
        failed += 1


# ─────────────────────────────────────────────────────────────────────────────
# 1. Behavioral Score Tests
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[1] Behavioral Score Service{RESET}")
from services.behavioral_service import (
    compute_behavioral_score, normalize_speech_rate,
    count_filler_words, normalize_filler_count
)

# Perfect candidate
result = compute_behavioral_score(1.0, 0.0, 0.0, 1.0, 0.5, 0.0, 1.0)
test("Perfect behavioral score ≈ 1.0",
     result["behavioral_score"] >= 0.95,
     f"Got {result['behavioral_score']}")

# Worst case
result = compute_behavioral_score(0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0)
test("Worst behavioral score ≈ 0.0",
     result["behavioral_score"] <= 0.05,
     f"Got {result['behavioral_score']}")

# Average candidate
result = compute_behavioral_score(0.6, 0.3, 0.2, 0.7, 0.4, 0.3, 0.7)
test("Average candidate score between 0.4 and 0.8",
     0.4 <= result["behavioral_score"] <= 0.8,
     f"Got {result['behavioral_score']}")

# Breakdown has all 6 keys
test("Breakdown has all 6 components",
     len(result["breakdown"]) == 6,
     f"Got {len(result['breakdown'])} keys")

# Speech rate normalization
test("Ideal speech rate (140 wpm) = 1.0",
     normalize_speech_rate(140) == 1.0)
test("Very slow speech rate (50 wpm) < 0.5",
     normalize_speech_rate(50) < 0.5)
test("Very fast speech rate (250 wpm) < 0.5",
     normalize_speech_rate(250) < 0.5)

# Filler word counting
sample_text = "um I think you know this is like basically correct"
count = count_filler_words(sample_text)
test("Filler word counter detects fillers",
     count >= 3, f"Detected {count} fillers")

norm = normalize_filler_count(5, 50)
test("10% filler ratio = 1.0 (max)",
     norm == 1.0, f"Got {norm}")

norm_low = normalize_filler_count(0, 100)
test("0% filler ratio = 0.0 (perfect)",
     norm_low == 0.0, f"Got {norm_low}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Resume Scoring Tests (no API calls — uses fallback skills)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[2] Resume Scoring Service{RESET}")
from services.resume_service import (
    parse_resume_skills, score_resume,
    estimate_experience_score, estimate_project_score
)

strong_resume = """
Senior Software Engineer with 4 years of experience.
Skills: Python, Machine Learning, Deep Learning, FastAPI, Docker,
PostgreSQL, React, TensorFlow, PyTorch, Git, AWS, Kubernetes.
Projects: Built a distributed ML pipeline deployed on AWS.
Developed an NLP-based recommendation system with REST API.
Internship at TechCorp, developed computer vision system.
Published open source project on GitHub with 200 stars.
"""

weak_resume = """
Student. Knows some basics.
Did a project once.
"""

# Parse skills
skills = parse_resume_skills(strong_resume)
test("Strong resume has multiple skills detected",
     len(skills) >= 5, f"Got {len(skills)} skills: {skills}")

weak_skills = parse_resume_skills(weak_resume)
test("Weak resume has fewer skills",
     len(weak_skills) < len(skills))

# Experience score
exp_strong = estimate_experience_score(strong_resume)
exp_weak   = estimate_experience_score(weak_resume)
test("Strong resume experience score > weak",
     exp_strong > exp_weak,
     f"Strong={exp_strong}, Weak={exp_weak}")
test("Experience score in [0, 1]",
     0.0 <= exp_strong <= 1.0)

# Project score
proj_strong = estimate_project_score(strong_resume)
proj_weak   = estimate_project_score(weak_resume)
test("Strong resume project score > weak",
     proj_strong > proj_weak,
     f"Strong={proj_strong}, Weak={proj_weak}")

# Full resume score
result = score_resume(strong_resume)
test("Resume score R in [0, 1]",
     0.0 <= result["resume_score"] <= 1.0,
     f"Got R={result['resume_score']}")
test("Market skill match M in [0, 1]",
     0.0 <= result["market_skill_match"] <= 1.0)
test("Has matched_skills list",
     isinstance(result["matched_skills"], list))
test("Has missing_skills list",
     isinstance(result["missing_skills"], list))
test("R = 0.4M + 0.3E + 0.3P (formula check)",
     abs(result["resume_score"] - (
         0.4 * result["market_skill_match"] +
         0.3 * result["experience_score"] +
         0.3 * result["project_score"]
     )) < 0.001)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Hiring Probability Tests
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[3] Hiring Probability Service{RESET}")
from services.hiring_service import predict_hiring_probability

# Strong candidate
result = predict_hiring_probability(
    technical_score=85.0,
    behavioral_score=0.85,
    resume_score=0.80,
    max_difficulty=4,
    eye_contact_pct=0.9,
    speech_rate_norm=0.8
)
test("Strong candidate recommended to Hire",
     result["recommendation"] == "Hire",
     f"Got '{result['recommendation']}' with prob={result['hiring_probability']}")
test("Hiring probability in [0, 1]",
     0.0 <= result["hiring_probability"] <= 1.0)

# Weak candidate
result_weak = predict_hiring_probability(
    technical_score=25.0,
    behavioral_score=0.2,
    resume_score=0.15,
    max_difficulty=1,
    eye_contact_pct=0.2,
    speech_rate_norm=0.3
)
test("Weak candidate recommended to Reject",
     result_weak["recommendation"] in ["Reject", "Maybe"],
     f"Got '{result_weak['recommendation']}'")
test("Strong prob > Weak prob",
     result["hiring_probability"] > result_weak["hiring_probability"])


# ─────────────────────────────────────────────────────────────────────────────
# 4. LLaMA Difficulty Progression Tests (no model needed)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[4] Difficulty Progression Logic{RESET}")
from services.llama_service import calculate_technical_score

# T = Σ(Si * Di) / Σ(Di)
scores      = [80, 60, 90]
difficulties = [1, 2, 3]
expected = (80*1 + 60*2 + 90*3) / (1+2+3)  # = 78.33
T = calculate_technical_score(scores, difficulties)
test("Weighted technical score formula correct",
     abs(T - expected) < 0.01,
     f"Expected {expected:.2f}, Got {T}")

test("Empty scores returns 0.0",
     calculate_technical_score([], []) == 0.0)

test("Single question score",
     calculate_technical_score([75], [2]) == 75.0)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Emotion Stability Tests
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[5] Emotion Stability Service{RESET}")
from services.emotion_service import compute_emotion_stability

stable_emotions   = ["neutral", "neutral", "happy", "neutral", "neutral"]
unstable_emotions = ["angry", "fear", "sad", "angry", "disgust"]
mixed_emotions    = ["neutral", "happy", "neutral", "sad", "neutral"]

stable_score   = compute_emotion_stability(stable_emotions)
unstable_score = compute_emotion_stability(unstable_emotions)
mixed_score    = compute_emotion_stability(mixed_emotions)

test("Stable emotions score > 0.7",
     stable_score > 0.7, f"Got {stable_score}")
test("Unstable emotions score < 0.5",
     unstable_score < 0.5, f"Got {unstable_score}")
test("Mixed emotions score between unstable and stable",
     unstable_score <= mixed_score <= stable_score,
     f"unstable={unstable_score}, mixed={mixed_score}, stable={stable_score}")
test("Empty emotion history returns 0.5",
     compute_emotion_stability([]) == 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# 6. GPU Manager Tests
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[6] GPU Manager Utility{RESET}")
from utils.gpu_manager import get_gpu_memory_info, clear_gpu_cache, SequentialGPUContext

mem = get_gpu_memory_info()
test("GPU memory info returns a dict",
     isinstance(mem, dict))
test("GPU info has 'available' key",
     "available" in mem)

# Context manager should work without errors
try:
    with SequentialGPUContext("test_model"):
        pass
    test("SequentialGPUContext runs without error", True)
except Exception as e:
    test("SequentialGPUContext runs without error", False, str(e))

# clear_gpu_cache should not raise
try:
    clear_gpu_cache()
    test("clear_gpu_cache() runs without error", True)
except Exception as e:
    test("clear_gpu_cache() runs without error", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{'='*50}")
print(f"  Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET} / {total} total")
print(f"{'='*50}\n")

if failed == 0:
    print(f"{GREEN}All tests passed! Backend logic is correct.{RESET}\n")
else:
    print(f"{RED}{failed} test(s) failed. Check the output above.{RESET}\n")
    sys.exit(1)
