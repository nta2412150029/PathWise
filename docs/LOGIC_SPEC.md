Logic Specification
1. Core Data
Each skill has the following attributes:
Field
Meaning
Scale
Current Level
User's current proficiency
1–5
Required Level
Level required by the target career
1–5
Importance
Importance of the skill for the target career
0–100
Demand
Market demand for the skill
0–100
Strategic Value
Value of the skill as a prerequisite or as a skill that unlocks other skills
0–100

The last three attributes (Importance, Demand, and Strategic Value) use a 0–100 scale instead of 1–5 for the following reasons:
Granular Weighting for the Final Score: The system calculates a final Priority Score and Career Fit as percentages (e.g., 72.6% or 91%). A 0–100 scale provides the necessary mathematical granularity to act as weights or percentage inputs in the final algorithm (Priority Score = 0.30*G + 0.30*I + 0.20*D + 0.20*P).
Metric Distinctness: The 1–5 scale is explicitly reserved to represent the project's human-readable proficiency framework (Beginner → Basic → Intermediate → Advanced → Expert). Metrics like Market Demand or Strategic Value do not fit this proficiency framework and are better represented as percentile scores or percentages.
Formula Normalization: To make the math work evenly, the system actually takes the 1–5 "Skill Gap" and normalizes it into a 0–100 "Gap Score" (using the formula Gap / 4 * 100). This ensures all variables are on the same 100-point baseline before they are multiplied by their respective weights (30%, 20%, etc.) to generate the final recommendation.
The 1–5 skill scale follows the project brief's Beginner → Basic → Intermediate → Advanced → Expert framework.
2. Skill Gap
The basic skill gap is:
Gap=RequiredLevel−CurrentLevel
For implementation, negative gaps are treated as zero:
Gap=max⁡(RequiredLevel−CurrentLevel,0)
This prevents a student who is already above the required level from receiving a negative learning requirement.
Example
Skill
Current
Required
Gap
SQL
1
3
2
Power BI
1
3
2
Statistics
3
3
0
Excel
4
4
0

This follows the project's central comparison between current skill level and career-required skill level.
3. Normalized Skill Gap Score
Because the Priority Score combines different variables on a 0–100 scale, the raw gap should be normalized.

Why 4?
Because the skill scale runs from 1 to 5, so the maximum possible difference is:
5−1=4
Therefore:

Skill
Gap
Gap Score
SQL
2
50
Power BI
2
50
Statistics
0
0

This is an implementation choice for the MVP; the original brief defines the gap concept but does not prescribe a normalization formula.
4. Career Fit Score
The brief explicitly proposes a weighted Career Fit formula:

We need to define SkillMatch.
For the MVP:

This means:
meeting the requirement = 100%;
being below the requirement = partial match;
exceeding the requirement does not push the score above 100%.
Example
Suppose:
Skill
Current
Required
Skill Match
Excel
4
4
100%
Communication
4
4
100%
Presentation
4
4
100%
Statistics
3
4
75%
SQL
1
3
33.3%
Power BI
1
3
33.3%

Then:

This produces a model-based overall indicator, consistent with the brief's example of presenting Career Fit as something like 72%, rather than claiming that the score literally means "72% qualified for a job."
5. Skill Priority Score
This is the most important algorithm in the project.
The brief proposes:

where:
G = Skill Gap
I = Career Importance
D = Market Demand
P = Prerequisite / Strategic Value.
The brief does not specify the weights. For the MVP, I recommend:
PriorityScore=0.30G+0.30I+0.20D+0.20P
So:
30% Gap
30% Career Importance
20% Market Demand
20% Strategic Value
This keeps the algorithm explainable while giving slightly more emphasis to the two things most directly related to the user's learning decision.
Interestingly, these weights also reproduce the brief's illustrative SQL example very closely:
0.3(90)+0.3(95)+0.2(90)+0.2(85)=90.5≈91
which matches the example Priority Score of 91% in the project document.
6. Recommendation Logic
The recommendation should not simply select the skill with the highest Priority Score.
The system should follow these steps:
Step 1 — Identify skill gaps
Only skills with:
Gap>0
become learning candidates.
Step 2 — Calculate Priority Score
Calculate:
PriorityScore=0.30G+0.30I+0.20D+0.20P

for each candidate.
Step 3 — Check prerequisites
If Skill B requires Skill A, and the user has not reached the required level for Skill A, Skill B is considered blocked.
For example:
SQL
 ↓
Power BI
If:
SQL = 1/3
Power BI = 1/3
then both have gaps, but Power BI should not be recommended before SQL because SQL is its prerequisite.
This directly follows the project's idea that skills are not independent and that prerequisites should affect the learning path.
Step 4 — Recommend the highest-priority unblocked skill
The system recommends:
the highest-priority skill that the user can logically learn next.
This makes the recommendation more defensible than simply sorting by score.
7. Learning Roadmap
The roadmap follows prerequisite order first, then priority among skills that are currently available.
Example:
Current Skill Profile
        ↓
SQL Fundamentals
        ↓
SQL Intermediate
        ↓
Power BI
        ↓
Business Analytics Project
        ↓
Target Career
This is consistent with the roadmap and prerequisite structures described in the original project brief.
8. Complete Example
Let's create one fictional user:
User
Target Career: Business Analyst
Skill
Current
Required
Importance
Demand
Strategic Value
SQL
1
3
95
90
85
Power BI
1
3
80
85
70
Statistics
3
3
75
80
50
Excel
4
4
90
75
40
Communication
4
4
85
60
30

Skill Gap
SQL       → 3 - 1 = 2
Power BI  → 3 - 1 = 2
Statistics → 3 - 3 = 0
Excel      → 4 - 4 = 0
Communication → 4 - 4 = 0
Priority Scores
SQL:
0.3(50)+0.3(95)+0.2(90)+0.2(85)=78.5
Power BI:
0.3(50)+0.3(80)+0.2(85)+0.2(70)=70
Therefore:
SQL       → 78.5
Power BI  → 70.0
But there is another important rule:
SQL → prerequisite → Power BI
So even if Power BI had a high score, SQL must come first.
System output
Current Career Fit: ~72.6%

Top Skill Gap:
SQL

Priority Score:
78.5%

Why SQL?
• High skill gap
• High career importance
• High market demand
• High strategic value
• Required before Power BI

Recommended Next Skill:
SQL
This is exactly the kind of explanation the original brief wants the system to be able to provide: not just “Learn SQL”, but why the algorithm reached that recommendation.
9. Python Pseudocode
This is the logic your Python component ultimately needs to implement:
for skill in skills:
    gap = max(required[skill] - current[skill], 0)
    gap_score = gap / 4 * 100

    skill_match = min(current[skill] / required[skill], 1) * 100

    priority = (
        0.30 * gap_score
        + 0.30 * importance[skill]
        + 0.20 * demand[skill]
        + 0.20 * strategic_value[skill]
    )
Then:
candidates = [skill for skill in skills if gap[skill] > 0]
Then apply prerequisite logic and select the highest-priority unblocked candidate.
10. Scope Decision for MVP
Mình đề nghị bạn chốt chính thức Task 2 như sau:
MVP
Skill Gap
→ Required - Current
Career Fit
→ weighted average of skill matches
Skill Priority
→ 30% Gap + 30% Importance + 20% Demand + 20% Strategic Value
Recommendation
→ highest-priority skill that is not blocked by an unmet prerequisite
Learning Roadmap
→ prerequisite-aware sequence toward target career
Not MVP
Không đưa clustering, prediction, advanced ML, What-if simulation, time optimization vào logic core lúc này. Project brief cũng đặt các phần clustering/prediction ở các level nâng cao hơn và nói rõ không nhất thiết cần Level 5 prediction cho MVP.
The 91% SQL example in the original concept document is illustrative. For implementation, use the normalized Gap Score defined in the team's Logic Specification.
