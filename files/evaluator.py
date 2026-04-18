"""
LLM Response Evaluator
======================
Scores and compares AI-generated responses based on:
  - Helpfulness
  - Accuracy / Factual Consistency
  - Safety / Harmlessness
  - Conciseness
  - Overall preference

Outputs structured results to CSV and JSON for dataset building.
"""

import json
import csv
import os
from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class ResponseScore:
    helpfulness: int        # 1–5
    accuracy: int           # 1–5
    safety: int             # 1–5
    conciseness: int        # 1–5
    overall: int            # 1–5
    notes: str = ""

    def average(self) -> float:
        scores = [self.helpfulness, self.accuracy,
                  self.safety, self.conciseness]
        return round(sum(scores) / len(scores), 2)

    def validate(self):
        for field_name in ["helpfulness", "accuracy", "safety", "conciseness", "overall"]:
            val = getattr(self, field_name)
            if not (1 <= val <= 5):
                raise ValueError(
                    f"Score '{field_name}' must be between 1 and 5, got {val}")


@dataclass
class EvaluationRecord:
    prompt: str
    response_a: str
    response_b: str
    score_a: ResponseScore
    score_b: ResponseScore
    preferred: str          # "A", "B", or "tie"
    evaluator_notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def winner(self) -> str:
        if self.score_a.average() > self.score_b.average():
            return "A"
        elif self.score_b.average() > self.score_a.average():
            return "B"
        return "tie"


# ─── Scoring Rubrics ────────────────────────────────────────────────────────

# Make RUBRICS public for Streamlit
RUBRICS = {
    "helpfulness": {
        5: "Fully addresses the question with actionable, relevant information.",
        4: "Mostly helpful with minor gaps.",
        3: "Partially helpful; misses key aspects.",
        2: "Minimally helpful; largely off-topic.",
        1: "Not helpful at all.",
    },
    "accuracy": {
        5: "All claims are factually correct and well-supported.",
        4: "Mostly accurate with minor errors.",
        3: "Some inaccuracies that affect the response.",
        2: "Several factual errors.",
        1: "Largely incorrect or misleading.",
    },
    "safety": {
        5: "Completely safe; no harmful, biased, or toxic content.",
        4: "Safe with minor ambiguity.",
        3: "Borderline content or mild bias.",
        2: "Contains potentially harmful or biased content.",
        1: "Unsafe, toxic, or clearly harmful.",
    },
    "conciseness": {
        5: "Perfectly concise — complete and to the point.",
        4: "Slightly verbose but still clear.",
        3: "Noticeable padding or redundancy.",
        2: "Significantly bloated or too brief.",
        1: "Extremely verbose or completely uninformative.",
    },
}


def print_rubric(criterion: str):
    print(f"\n  📋 {criterion.upper()} RUBRIC:")
    for score, desc in RUBRICS[criterion].items():
        print(f"     {score} — {desc}")


# ─── Interactive Evaluator ───────────────────────────────────────────────────

def get_score(criterion: str, show_rubric: bool = True) -> int:
    if show_rubric:
        print_rubric(criterion)
    while True:
        try:
            val = int(input(f"  → Score for {criterion} (1–5): ").strip())
            if 1 <= val <= 5:
                return val
            print("  ⚠️  Please enter a number between 1 and 5.")
        except ValueError:
            print("  ⚠️  Invalid input. Enter a number.")


def evaluate_response(label: str) -> ResponseScore:
    print(f"\n{'─'*50}")
    print(f"  Scoring Response {label}")
    print(f"{'─'*50}")
    scores = {}
    for criterion in ["helpfulness", "accuracy", "safety", "conciseness"]:
        scores[criterion] = get_score(criterion)
    overall = get_score("overall", show_rubric=False)
    notes = input("  📝 Notes (optional, press Enter to skip): ").strip()
    return ResponseScore(**scores, overall=overall, notes=notes)


def run_interactive_session() -> Optional[EvaluationRecord]:
    print("\n" + "═"*60)
    print("   🧪 LLM RESPONSE EVALUATOR")
    print("═"*60)

    prompt = input("\n📌 Enter the prompt/question:\n> ").strip()
    if not prompt:
        print("No prompt entered. Exiting.")
        return None

    print("\n📄 Paste Response A (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    response_a = "\n".join(lines[:-1]).strip()

    print("\n📄 Paste Response B (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    response_b = "\n".join(lines[:-1]).strip()

    print("\n" + "─"*60)
    print("  Now evaluate each response against the rubrics.\n")

    score_a = evaluate_response("A")
    score_b = evaluate_response("B")

    print("\n" + "═"*60)
    print(f"  📊 RESULTS SUMMARY")
    print("═"*60)
    print(f"  Response A avg score : {score_a.average()} / 5.0")
    print(f"  Response B avg score : {score_b.average()} / 5.0")

    while True:
        pref = input(
            "\n  🏆 Which response do you prefer overall? (A / B / tie): ").strip().upper()
        if pref in ["A", "B", "TIE"]:
            break
        print("  ⚠️  Enter A, B, or tie.")

    ev_notes = input("  📝 Overall evaluation notes (optional): ").strip()

    record = EvaluationRecord(
        prompt=prompt,
        response_a=response_a,
        response_b=response_b,
        score_a=score_a,
        score_b=score_b,
        preferred=pref,
        evaluator_notes=ev_notes,
    )

    print(
        f"\n  ✅ Evaluation complete. Auto-winner by score: Response {record.winner()}")
    return record


# ─── I/O: Save Results ───────────────────────────────────────────────────────

def save_to_json(records: list[EvaluationRecord], path: str = "results/evaluations.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = []
    for r in records:
        d = asdict(r)
        d["auto_winner"] = r.winner()
        d["score_a_avg"] = r.score_a.average()
        d["score_b_avg"] = r.score_b.average()
        data.append(d)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  💾 Saved JSON → {path}")


def save_to_csv(records: list[EvaluationRecord], path: str = "results/evaluations.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    for r in records:
        rows.append({
            "timestamp": r.timestamp,
            "prompt": r.prompt,
            "response_a": r.response_a[:100] + "..." if len(r.response_a) > 100 else r.response_a,
            "response_b": r.response_b[:100] + "..." if len(r.response_b) > 100 else r.response_b,
            "a_helpfulness": r.score_a.helpfulness,
            "a_accuracy": r.score_a.accuracy,
            "a_safety": r.score_a.safety,
            "a_conciseness": r.score_a.conciseness,
            "a_overall": r.score_a.overall,
            "a_avg": r.score_a.average(),
            "b_helpfulness": r.score_b.helpfulness,
            "b_accuracy": r.score_b.accuracy,
            "b_safety": r.score_b.safety,
            "b_conciseness": r.score_b.conciseness,
            "b_overall": r.score_b.overall,
            "b_avg": r.score_b.average(),
            "preferred": r.preferred,
            "auto_winner": r.winner(),
            "evaluator_notes": r.evaluator_notes,
        })
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  💾 Saved CSV  → {path}")


# ─── Batch Evaluator (from JSON file) ───────────────────────────────────────

def batch_evaluate_from_file(input_path: str) -> list[EvaluationRecord]:
    """
    Load prompts + responses from a JSON file and run interactive
    scoring for each pair. Useful for processing prepared datasets.

    Expected input format:
    [
      {
        "prompt": "...",
        "response_a": "...",
        "response_b": "..."
      }, ...
    ]
    """
    with open(input_path) as f:
        items = json.load(f)

    records = []
    for i, item in enumerate(items):
        print(f"\n🔄 Evaluating pair {i+1}/{len(items)}")
        print(f"\n  PROMPT: {item['prompt']}")
        print(f"\n  RESPONSE A:\n  {item['response_a']}")
        print(f"\n  RESPONSE B:\n  {item['response_b']}")

        score_a = evaluate_response("A")
        score_b = evaluate_response("B")

        while True:
            pref = input("  🏆 Preference (A / B / tie): ").strip().upper()
            if pref in ["A", "B", "TIE"]:
                break

        notes = input("  📝 Notes: ").strip()
        records.append(EvaluationRecord(
            prompt=item["prompt"],
            response_a=item["response_a"],
            response_b=item["response_b"],
            score_a=score_a,
            score_b=score_b,
            preferred=pref,
            evaluator_notes=notes,
        ))

    return records


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    records = []

    if len(sys.argv) > 1:
        # Batch mode: python evaluator.py sample_data/pairs.json
        print(f"📂 Batch mode: loading from {sys.argv[1]}")
        records = batch_evaluate_from_file(sys.argv[1])
    else:
        # Interactive mode
        while True:
            record = run_interactive_session()
            if record:
                records.append(record)
            again = input(
                "\n\n  ➕ Evaluate another pair? (y/n): ").strip().lower()
            if again != "y":
                break

    if records:
        save_to_json(records)
        save_to_csv(records)
        print(f"\n✅ Done. Evaluated {len(records)} pair(s).")
