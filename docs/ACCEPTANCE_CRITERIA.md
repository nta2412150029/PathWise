# PathWise — Acceptance Criteria

Manual verification checklist for the MVP. Each item should be tested against the demo user + Business Analyst career unless noted.

---

## Foundation Layer (Phase 1–2)

- [ ] `py -m pytest tests/ -v` — all tests pass with no failures
- [ ] `py src/api.py` starts without errors and prints the startup message
- [ ] `GET /api/skills` returns 20 skills in JSON
- [ ] `GET /api/careers` returns 4 careers in JSON
- [ ] `GET /api/user/skills` returns 20 skill entries
- [ ] `GET /api/analysis?career_id=1` returns a valid JSON response with `career_fit`, `recommendation`, and `skill_analysis`
- [ ] `GET /api/roadmap?career_id=1` returns a valid JSON response with a non-empty `roadmap` array
- [ ] Opening `http://localhost:5000` in a browser shows the Dashboard skeleton (no console errors)

---

## Scoring Logic

- [ ] `career_fit` for demo user + Business Analyst is approximately **70–72%**
- [ ] `career_fit` for demo user + Data Analyst is approximately **55–58%**
- [ ] Recommended skill for Business Analyst is **Business Process Analysis**
- [ ] Recommended skill for Data Analyst is **SQL**
- [ ] Recommended skill for Marketing Analyst is **Google Analytics**
- [ ] Recommended skill for Financial Analyst is **Excel**
- [ ] Power BI appears as **blocked** (by SQL) in Business Analyst analysis
- [ ] Power BI appears as **blocked** (by SQL) in Data Analyst analysis
- [ ] Machine Learning appears as **blocked** (by Python and Statistics) in Data Analyst analysis
- [ ] Financial Modeling appears as **blocked** (by Excel) in Financial Analyst analysis

---

## Roadmap Logic

- [ ] Business Analyst roadmap: SQL appears **before** Power BI
- [ ] Data Analyst roadmap: SQL appears first; Python and Data Visualization appear before their dependents
- [ ] Financial Analyst roadmap: Excel appears **before** Financial Modeling
- [ ] Skills with no gap (e.g., Communication at level 4 with required level 4) do **not** appear in the roadmap

---

## Skill Level Update

- [ ] `POST /api/user/skills` with `{"skill_id": 1, "current_level": 3}` returns `{"ok": true}`
- [ ] After updating SQL to level 3, re-fetching Business Analyst analysis shows Power BI is **no longer blocked**
- [ ] Sending `current_level: 6` returns HTTP 400 error
- [ ] Sending an unknown `skill_id` returns HTTP 404 error

---

## Formula Verification (from LOGIC_SPEC §8)

| Formula | Input | Expected | Tolerance |
|---|---|---|---|
| `skill_gap` | required=3, current=1 | 2 | exact |
| `skill_gap` (no negative) | required=3, current=5 | 0 | exact |
| `gap_score` | gap=2 | 50.0 | exact |
| `skill_match` | current=1, required=3 | 33.3% | ±0.1 |
| `skill_match` (capped) | current=5, required=3 | 100% | exact |
| `priority_score` (SQL) | GapScore=50, I=95, D=90, P=85 | 78.5 | ±0.1 |
| `priority_score` (Power BI) | GapScore=50, I=80, D=85, P=70 | 70.0 | ±0.1 |
