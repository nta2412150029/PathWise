# PathWise — Build Brief

## 1. Product

PathWise is a data-driven web application that analyzes a student's current skills against a target career profile and recommends which skill the student should learn next.

Core question:

"Given where I am now and where I want to go, what should I learn next?"

## 2. MVP User Flow

The MVP follows this flow:

1. Build Skill Profile
2. Choose Career Goal
3. Analyze Skill Gaps
4. Calculate Career Fit
5. Prioritize Skills
6. Recommend Next Skill
7. Display Learning Roadmap

The system should provide a clear explanation for why a skill is recommended.

## 3. MVP Pages

The MVP contains five main pages:

1. Dashboard
2. My Skills
3. Career Explorer
4. Skill Gap
5. Learning Roadmap

## 4. Core Data

The MVP uses:

- skills
- careers
- career skill requirements
- user skill levels
- skill prerequisites
- market demand
- strategic value

## 5. Core Logic

### Skill Gap

Gap = max(Required Level - Current Level, 0)

### Gap Score

GapScore = Gap / 4 * 100

### Skill Match

SkillMatch = min(Current Level / Required Level, 1) * 100

### Career Fit

CareerFit =
sum(SkillMatch * Importance) / sum(Importance)

### Skill Priority

PriorityScore =
0.30 * GapScore
+ 0.30 * Importance
+ 0.20 * Market Demand
+ 0.20 * Strategic Value

## 6. Recommendation Rule

Only skills with Gap > 0 are learning candidates.

Among candidates, recommend the highest-priority skill that is not blocked by an unmet prerequisite.

A skill with an unmet prerequisite must not be recommended before that prerequisite.

## 7. Learning Roadmap

The roadmap should respect prerequisite relationships.

Example:

SQL Fundamentals
→ SQL Intermediate
→ Power BI
→ Analytics Project

## 8. Important Scope Rule

This is an MVP.

Do NOT implement the following unless the core MVP is already stable:

- advanced machine learning prediction
- clustering
- complex personalization
- advanced What-If simulation
- time-based learning optimization

## 9. Vibecode Development Model

The website should be developed using Antigravity as an agentic coding environment.

Expected workflow:

1. Agent reads project context
2. Agent proposes implementation plan
3. Agent generates code
4. Human reviews changes
5. Agent runs tests
6. Human verifies behavior
7. Agent fixes issues
8. Changes are committed to GitHub

Do not manually build the website component-by-component unless required.

## 10. Recommended MVP Principle

Prefer the simplest architecture that allows:

- a working web interface
- Python-based data processing
- reproducible recommendation logic
- easy local execution
- easy GitHub sharing
- easy demonstration in the final video

Avoid unnecessary infrastructure, authentication systems, databases, external APIs, or advanced deployment architecture.

## 11. Source-of-Truth Rule

PRODUCT_SPEC.md defines product scope.

LOGIC_SPEC.md defines mathematical logic.

BUILD_BRIEF.md defines implementation constraints.

The agent must not invent new product features or alter the scoring formulas without explicit human approval.