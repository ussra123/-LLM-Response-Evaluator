"""
Analyze and visualize evaluation results from evaluations.json
Run after collecting evaluations: python analyze_results.py
"""

import json
import os
from collections import Counter


def load_results(path: str = "results/evaluations.json") -> list[dict]:
    if not os.path.exists(path):
        print(f"❌ No results file found at {path}")
        print("   Run evaluator.py first to generate results.")
        return []
    with open(path) as f:
        return json.load(f)


def print_bar(label: str, value: float, max_val: float = 5.0, width: int = 30):
    filled = int((value / max_val) * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:<15} [{bar}] {value:.2f}")


def analyze(records: list[dict]):
    if not records:
        return

    n = len(records)
    print("\n" + "═"*55)
    print("  📊 EVALUATION ANALYSIS REPORT")
    print("═"*55)
    print(f"  Total evaluations : {n}")

    # Preference distribution
    prefs = Counter(r["preferred"] for r in records)
    print(f"\n  🏆 Preference Distribution:")
    for pref, count in prefs.most_common():
        pct = count / n * 100
        print(f"     Response {pref:<4}: {count} ({pct:.1f}%)")

    # Agreement: manual preference vs auto-winner
    agreements = sum(
        1 for r in records if r["preferred"] == r["auto_winner"]
    )
    print(f"\n  🤝 Human vs Auto-score Agreement: {agreements}/{n} ({agreements/n*100:.1f}%)")

    # Average scores per dimension
    dims = ["helpfulness", "accuracy", "safety", "conciseness", "overall"]
    print(f"\n  📈 Average Scores — Response A:")
    for dim in dims:
        avg = sum(r["score_a"][dim] for r in records) / n
        print_bar(dim, avg)

    print(f"\n  📈 Average Scores — Response B:")
    for dim in dims:
        avg = sum(r["score_b"][dim] for r in records) / n
        print_bar(dim, avg)

    # Head-to-head
    print(f"\n  ⚖️  Head-to-Head (avg total scores):")
    avg_a = sum(r["score_a_avg"] for r in records) / n
    avg_b = sum(r["score_b_avg"] for r in records) / n
    print_bar("Response A", avg_a)
    print_bar("Response B", avg_b)

    # Notes
    notes = [r["evaluator_notes"] for r in records if r.get("evaluator_notes")]
    if notes:
        print(f"\n  📝 Evaluator Notes ({len(notes)} entries):")
        for i, note in enumerate(notes[:5], 1):
            print(f"     {i}. {note[:80]}{'...' if len(note) > 80 else ''}")

    print("\n" + "═"*55)
    print(f"  Results file: results/evaluations.json")
    print(f"  CSV export  : results/evaluations.csv")
    print("═"*55 + "\n")


if __name__ == "__main__":
    records = load_results()
    analyze(records)
