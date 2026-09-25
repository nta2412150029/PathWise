# PathWise

A data-driven career skill-gap advisor for university students.

> **Core question:** *"Given where I am now and where I want to go, what should I learn next?"*

---

## What It Does

PathWise compares a student's current skill profile against a target career's requirements and:

- Calculates **Skill Gaps** per skill
- Computes a **Career Fit Score** (%)
- Scores each gap skill with a **Priority Score** (gap × importance × demand × strategic value)
- Applies **prerequisite logic** to determine what can be learned next
- Recommends the **single best next skill** to learn
- Generates a **prerequisite-aware Learning Roadmap**

---

## Requirements

- Python 3.10 or later
- `py` launcher (Windows) **or** `python` / `python3` (Mac/Linux)

---

## Local Setup (first time)

```bash
# 1. Clone the repo
git clone <repo-url>
cd PathWise

# 2. (Recommended) Create a virtual environment
py -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Install dependencies
py -m pip install -r requirements.txt
```

---

## Run the Application

```bash
py src/api.py
```

Then open your browser at: **http://localhost:5000**

The server loads all CSV data from `data/` at startup and serves the web UI from `web/`.

---

## Run the Tests

```bash
py -m pytest tests/ -v
```

Expected output: all tests pass.

---

## Project Structure

```
PathWise/
│
├── data/                          # CSV source-of-truth files (edit here to change data)
│   ├── skills.csv                 # 20 skills across 4 categories
│   ├── careers.csv                # 4 target careers
│   ├── career_requirements.csv   # Skill requirements per career (importance, demand, strategic value)
│   ├── prerequisites.csv          # Prerequisite relationships between skills
│   └── demo_user_skills.csv      # Demo user's current skill levels (1–5)
│
├── src/
│   ├── engine.py                  # Core scoring logic (formulas, recommendation, roadmap)
│   ├── data_loader.py             # CSV readers and writer
│   └── api.py                     # Flask server + JSON API endpoints
│
├── web/                           # Frontend (HTML/CSS/JS — served by Flask)
│   ├── index.html                 # Dashboard
│   ├── skills.html                # My Skills
│   ├── careers.html               # Career Explorer
│   ├── gap.html                   # Skill Gap + Recommendation
│   ├── roadmap.html               # Learning Roadmap
│   ├── style.css                  # Shared styles
│   └── app.js                     # Frontend logic (fetch API)
│
├── tests/
│   ├── test_engine.py             # Unit tests for scoring formulas
│   └── test_data_loader.py        # Unit tests for CSV loading
│
├── docs/
│   ├── PRODUCT_SPEC.md            # Product scope and user flow
│   ├── LOGIC_SPEC.md              # Mathematical formulas (source of truth)
│   ├── BUILD_BRIEF.md             # Implementation constraints
│   └── ACCEPTANCE_CRITERIA.md    # Test cases for manual verification
│
├── requirements.txt               # Python dependencies
└── .gitignore
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/skills` | GET | All skills |
| `/api/careers` | GET | All careers |
| `/api/user/skills` | GET | Demo user's current skill levels |
| `/api/user/skills` | POST | Update one skill level `{"skill_id": 1, "current_level": 3}` |
| `/api/analysis?career_id=1` | GET | Full gap analysis, career fit %, recommendation |
| `/api/roadmap?career_id=1` | GET | Prerequisite-ordered learning roadmap |

---

## Scoring Formulas

All formulas are locked per `docs/LOGIC_SPEC.md`. Do not alter without explicit approval.

```
Gap          = max(required_level - current_level, 0)
GapScore     = Gap / 4 × 100
SkillMatch   = min(current_level / required_level, 1) × 100
CareerFit    = Σ(SkillMatch × importance) / Σ(importance)
PriorityScore = 0.30×GapScore + 0.30×importance + 0.20×market_demand + 0.20×strategic_value
```

---

## Demo User

The demo user's skills are stored in `data/demo_user_skills.csv`.
The web UI allows live editing of skill levels — changes persist to this file.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask |
| Data | CSV files (no database) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Tests | pytest |
