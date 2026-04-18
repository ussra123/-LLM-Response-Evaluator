"""
Streamlit Web UI for LLM Response Evaluator.
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from evaluator import ResponseScore, EvaluationRecord, RUBRICS, save_to_json, save_to_csv

# Page config
st.set_page_config(
    page_title="🧪 LLM Response Evaluator",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 LLM Response Evaluator")
st.markdown("**Web UI** - Score and compare AI responses across rubrics.")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose page", ["Single Evaluation", "View Results", "Analyze"])

if page == "Single Evaluation":
    st.header("📝 Single Evaluation")

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        prompt = st.text_area("📌 Prompt/Question", height=100, key="prompt")
    with col2:
        st.info("**Scoring Rubrics**")
        criterion = st.selectbox("View rubric", RUBRICS.keys())
        with st.expander(f"📋 {criterion.upper()}"):
            for score, desc in RUBRICS[criterion].items():
                st.write(f"**{score}** — {desc}")

    st.subheader("Responses")
    col_a, col_b = st.columns(2)
    with col_a:
        response_a = st.text_area("📄 Response A", height=200, key="resp_a")
    with col_b:
        response_b = st.text_area("📄 Response B", height=200, key="resp_b")

    # Scores A
    st.subheader("Score Response A")
    score_a_data = {}
    for criterion in ["helpfulness", "accuracy", "safety", "conciseness"]:
        score_a_data[criterion] = st.slider(
            f"{criterion.title()} (1-5)",
            1, 5, 3,
            help=RUBRICS[criterion][3],
            key=f"a_{criterion}"
        )
    a_overall = st.slider("Overall A", 1, 5, 3, key="a_overall")
    a_notes = st.text_area("Notes A", key="a_notes")

    # Scores B
    st.subheader("Score Response B")
    score_b_data = {}
    for criterion in ["helpfulness", "accuracy", "safety", "conciseness"]:
        score_b_data[criterion] = st.slider(
            f"{criterion.title()} (1-5)",
            1, 5, 3,
            help=RUBRICS[criterion][3],
            key=f"b_{criterion}"
        )
    b_overall = st.slider("Overall B", 1, 5, 3, key="b_overall")
    b_notes = st.text_area("Notes B", key="b_notes")

    # Preference & Submit
    col_pref1, col_pref2, col_pref3 = st.columns(3)
    preferred = col_pref1.radio(
        "🏆 Preferred", ["A", "B", "tie"], key="preferred")
    ev_notes = st.text_area("Overall Notes", key="ev_notes")

    if st.button("✅ Submit Evaluation", type="primary"):
        if prompt and response_a and response_b:
            # Create scores
            score_a = ResponseScore(
                **score_a_data, overall=a_overall, notes=a_notes
            )
            score_b = ResponseScore(
                **score_b_data, overall=b_overall, notes=b_notes
            )

            # Create record
            record = EvaluationRecord(
                prompt=prompt,
                response_a=response_a,
                response_b=response_b,
                score_a=score_a,
                score_b=score_b,
                preferred=preferred,
                evaluator_notes=ev_notes
            )

            # Load existing or create
            results_path = "results/evaluations.json"
            records = []
            if os.path.exists(results_path):
                with open(results_path) as f:
                    records = json.load(f)

            # Convert new record to dict and append
            from dataclasses import asdict
            new_entry = asdict(record)
            new_entry["auto_winner"] = record.winner()
            new_entry["score_a_avg"] = record.score_a.average()
            new_entry["score_b_avg"] = record.score_b.average()
            records.append(new_entry)

            # Save
            os.makedirs("results", exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(records, f, indent=2)

            # Also save CSV
            import csv
            csv_path = "results/evaluations.csv"
            csv_rows = []
            for r in records:
                csv_rows.append({
                    "timestamp": r.get("timestamp", ""),
                    "prompt": r["prompt"],
                    "response_a": r["response_a"][:100] + "..." if len(r["response_a"]) > 100 else r["response_a"],
                    "response_b": r["response_b"][:100] + "..." if len(r["response_b"]) > 100 else r["response_b"],
                    "a_helpfulness": r["score_a"]["helpfulness"],
                    "a_accuracy": r["score_a"]["accuracy"],
                    "a_safety": r["score_a"]["safety"],
                    "a_conciseness": r["score_a"]["conciseness"],
                    "a_overall": r["score_a"]["overall"],
                    "a_avg": r["score_a_avg"],
                    "b_helpfulness": r["score_b"]["helpfulness"],
                    "b_accuracy": r["score_b"]["accuracy"],
                    "b_safety": r["score_b"]["safety"],
                    "b_conciseness": r["score_b"]["conciseness"],
                    "b_overall": r["score_b"]["overall"],
                    "b_avg": r["score_b_avg"],
                    "preferred": r["preferred"],
                    "auto_winner": r["auto_winner"],
                    "evaluator_notes": r.get("evaluator_notes", ""),
                })
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
                writer.writeheader()
                writer.writerows(csv_rows)

            st.success("✅ Evaluation saved!")
            st.balloons()

            # Summary
            st.subheader("📊 Summary")
            col_sum1, col_sum2 = st.columns(2)
            with col_sum1:
                st.metric("A Avg", score_a.average())
                st.metric("A Winner?", "Yes" if record.winner() == "A" else "No")
            with col_sum2:
                st.metric("B Avg", score_b.average())
                st.metric("B Winner?", "Yes" if record.winner() == "B" else "No")
        else:
            st.error("❌ Please fill all response fields.")

elif page == "View Results":
    st.header("📂 View Results")
    if os.path.exists("results/evaluations.json"):
        df = pd.read_json("results/evaluations.json")
        st.dataframe(df, use_container_width=True)

        # Downloads
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("� Download JSON", data=open(
                "results/evaluations.json").read(), file_name="evaluations.json")
        with col_dl2:
            st.download_button("📥 Download CSV", data=open(
                "results/evaluations.csv").read(), file_name="evaluations.csv")
    else:
        st.info("ℹ️ No results yet. Run an evaluation first.")

elif page == "Analyze":
    st.header("📊 Analyze")
    from analyze_results import load_results

    records = load_results()
    if records:
        n = len(records)
        st.metric("Total Evaluations", n)

        from collections import Counter
        prefs = Counter(r["preferred"] for r in records)
        st.subheader("🏆 Preference Distribution")
        pref_data = {"Response": list(prefs.keys()), "Count": list(prefs.values())}
        st.bar_chart(pd.DataFrame(pref_data).set_index("Response"))

        agreements = sum(1 for r in records if r["preferred"] == r["auto_winner"])
        st.metric("Human vs Auto-score Agreement",
                  f"{agreements}/{n} ({agreements/n*100:.1f}%)")

        dims = ["helpfulness", "accuracy", "safety", "conciseness", "overall"]
        st.subheader("📈 Average Scores")
        avg_data = {
            "Dimension": dims,
            "Response A": [round(sum(r["score_a"][d] for r in records) / n, 2) for d in dims],
            "Response B": [round(sum(r["score_b"][d] for r in records) / n, 2) for d in dims],
        }
        st.dataframe(pd.DataFrame(avg_data).set_index("Dimension"), use_container_width=True)
    else:
        st.info("ℹ️ No results yet. Run an evaluation first.")
