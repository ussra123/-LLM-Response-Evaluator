# 🧪 LLM Response Evaluator

A simple tool for comparing and scoring AI-generated responses side by side. Give it a prompt and two AI answers, rate each one across four quality dimensions, and get structured results you can analyze or export.

Built to support AI evaluation workflows, RLHF dataset building, and model comparison.

---

## ✨ Features

- **Web UI** — score responses using sliders with built-in rubric guidance
- **CLI mode** — run evaluations directly from the terminal
- **Batch mode** — process a prepared dataset of prompt/response pairs at once
- **Auto-scoring** — automatically determines a winner based on average scores
- **Export** — saves results to JSON and CSV for further analysis
- **Analysis report** — view preference distributions, score averages, and human vs. auto agreement

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/ussra123/-LLM-Response-Evaluator.git
cd -LLM-Response-Evaluator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the Web UI

```bash
streamlit run streamlit_app.py
```

Then open your browser at `http://localhost:8501`.

---

## 🖥️ How to Use

### Web UI

1. Go to the **Evaluate** page
2. Enter your prompt and paste two AI responses (A and B)
3. Use the sliders to score each response on Helpfulness, Accuracy, Safety, and Conciseness
4. Select your preferred response and submit
5. View saved evaluations on the **Results** page
6. See charts and statistics on the **Analyze** page

### CLI (interactive)

```bash
python evaluator.py
```

Follow the prompts to enter a prompt, paste two responses, and score them.

### Batch mode

Prepare a JSON file with this format:

```json
[
  {
    "prompt": "Your question here",
    "response_a": "First AI response",
    "response_b": "Second AI response"
  }
]
```

Then run:

```bash
python evaluator.py sample_data/pairs.json
```

A sample file with 5 example pairs is included in `sample_data/pairs.json`.

### Analyze results (CLI)

```bash
python analyze_results.py
```

---

## 📊 Scoring Dimensions

Each response is scored 1–5 on four dimensions:

| Dimension       | What it measures                                        |
| --------------- | ------------------------------------------------------- |
| **Helpfulness** | Does the response fully address the question?           |
| **Accuracy**    | Are the facts correct and well-supported?               |
| **Safety**      | Is the content free of harmful or biased material?      |
| **Conciseness** | Is the response appropriately detailed without padding? |

**Score guide:**

| Score | Meaning                  |
| ----- | ------------------------ |
| 5     | Excellent                |
| 4     | Good, minor issues       |
| 3     | Acceptable, some gaps    |
| 2     | Poor, significant issues |
| 1     | Unacceptable             |

---

## 📁 Project Structure

```
-LLM-Response-Evaluator/
│
├── evaluator.py          # Core evaluation logic (interactive + batch)
├── streamlit_app.py      # Web UI
├── analyze_results.py    # CLI analysis and reporting
├── test_evaluator.py     # Unit tests
├── requirements.txt      # Python dependencies
│
├── sample_data/
│   └── pairs.json        # 5 example prompt/response pairs to try
│
└── results/              # Auto-created when you run an evaluation
    ├── evaluations.json
    └── evaluations.csv
```

---

## 📤 Output Format

Results are saved automatically after each evaluation.

**JSON** (`results/evaluations.json`) — full structured record per evaluation:

```json
{
  "prompt": "What is the capital of Australia?",
  "response_a": "...",
  "response_b": "...",
  "score_a": {
    "helpfulness": 2,
    "accuracy": 1,
    "safety": 5,
    "conciseness": 3,
    "overall": 2
  },
  "score_b": {
    "helpfulness": 5,
    "accuracy": 5,
    "safety": 5,
    "conciseness": 5,
    "overall": 5
  },
  "preferred": "B",
  "auto_winner": "B",
  "score_a_avg": 2.75,
  "score_b_avg": 5.0
}
```

**CSV** (`results/evaluations.csv`) — flat format, easy to open in Excel or load with pandas.

---

## 🧪 Running Tests

```bash
pytest test_evaluator.py -v
```

---

## 💡 Use Cases

- Building preference datasets for RLHF pipelines
- A/B testing outputs from different LLMs or prompt versions
- Quality auditing AI-generated content before publishing
- Research on human preference patterns in AI responses

---

## 📄 License

MIT
