"""
test_engine.py
Unit tests for all 9 PathWise engine functions.

Primary fixture: the exact example from LOGIC_SPEC.md §8
  Target career: Business Analyst
  Skills: SQL, Power BI, Statistics, Excel, Communication
  Prerequisite: Power BI requires SQL

All expected values in this file are derived directly from LOGIC_SPEC.md.
Do NOT adjust expected values without updating LOGIC_SPEC.md first.

Run with:  py -m pytest tests/test_engine.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine import (
    calculate_skill_gap,
    calculate_gap_score,
    calculate_skill_match,
    calculate_career_fit,
    calculate_priority_score,
    get_learning_candidates,
    check_prerequisite_block,
    recommend_next_skill,
    generate_learning_roadmap,
    compute_skill_analysis,    # internal helper — tested for api.py compatibility
)


# ===========================================================================
# Shared fixture: LOGIC_SPEC.md §8 sample data
# ===========================================================================

# Skill IDs used in the LOGIC_SPEC §8 example
_SQL       = 1
_POWER_BI  = 2
_STATS     = 3
_EXCEL     = 4
_COMM      = 5

@pytest.fixture
def logic_spec_career_reqs():
    """Career requirements exactly as given in LOGIC_SPEC.md §8."""
    return {
        _SQL:      {"required_level": 3, "importance": 95, "market_demand": 90, "strategic_value": 85},
        _POWER_BI: {"required_level": 3, "importance": 80, "market_demand": 85, "strategic_value": 70},
        _STATS:    {"required_level": 3, "importance": 75, "market_demand": 80, "strategic_value": 50},
        _EXCEL:    {"required_level": 4, "importance": 90, "market_demand": 75, "strategic_value": 40},
        _COMM:     {"required_level": 4, "importance": 85, "market_demand": 60, "strategic_value": 30},
    }


@pytest.fixture
def logic_spec_user_skills():
    """User profile exactly as given in LOGIC_SPEC.md §8."""
    return {
        _SQL:      1,   # gap = 2
        _POWER_BI: 1,   # gap = 2
        _STATS:    3,   # gap = 0  (no gap)
        _EXCEL:    4,   # gap = 0  (no gap)
        _COMM:     4,   # gap = 0  (no gap)
    }


@pytest.fixture
def logic_spec_prerequisites():
    """Power BI requires SQL (LOGIC_SPEC.md §8)."""
    return {_POWER_BI: [_SQL]}


@pytest.fixture
def logic_spec_skills_meta():
    return {
        _SQL:      {"skill_name": "SQL",           "category": "Technical"},
        _POWER_BI: {"skill_name": "Power BI",      "category": "Technical"},
        _STATS:    {"skill_name": "Statistics",    "category": "Technical"},
        _EXCEL:    {"skill_name": "Excel",         "category": "Technical"},
        _COMM:     {"skill_name": "Communication", "category": "Soft Skill"},
    }


# ===========================================================================
# 1. calculate_skill_gap  (LOGIC_SPEC §2)
# ===========================================================================

class TestCalculateSkillGap:
    def test_positive_gap(self):
        """SQL: required=3, current=1 → gap=2  (LOGIC_SPEC §8)"""
        assert calculate_skill_gap(required_level=3, current_level=1) == 2

    def test_zero_gap_when_equal(self):
        """Statistics: required=3, current=3 → gap=0  (LOGIC_SPEC §8)"""
        assert calculate_skill_gap(required_level=3, current_level=3) == 0

    def test_zero_gap_when_exceeded(self):
        """Gap must never be negative (LOGIC_SPEC §2)."""
        assert calculate_skill_gap(required_level=3, current_level=5) == 0

    def test_zero_gap_exact_match(self):
        """Excel: required=4, current=4 → gap=0  (LOGIC_SPEC §8)"""
        assert calculate_skill_gap(required_level=4, current_level=4) == 0

    def test_maximum_gap(self):
        """Scale is 1–5, so max gap = 4."""
        assert calculate_skill_gap(required_level=5, current_level=1) == 4

    def test_gap_of_one(self):
        assert calculate_skill_gap(required_level=4, current_level=3) == 1

    def test_all_logic_spec_gaps(self, logic_spec_career_reqs, logic_spec_user_skills):
        """Cross-check all five skills against §8."""
        expected = {_SQL: 2, _POWER_BI: 2, _STATS: 0, _EXCEL: 0, _COMM: 0}
        for sid, exp_gap in expected.items():
            req = logic_spec_career_reqs[sid]["required_level"]
            cur = logic_spec_user_skills[sid]
            assert calculate_skill_gap(req, cur) == exp_gap, f"skill_id={sid}"


# ===========================================================================
# 2. calculate_gap_score  (LOGIC_SPEC §3)
# ===========================================================================

class TestCalculateGapScore:
    def test_gap_2_gives_50(self):
        """LOGIC_SPEC §3: gap=2 → GapScore=50."""
        assert calculate_gap_score(2) == 50.0

    def test_gap_0_gives_0(self):
        assert calculate_gap_score(0) == 0.0

    def test_max_gap_gives_100(self):
        """Maximum gap of 4 → GapScore=100."""
        assert calculate_gap_score(4) == 100.0

    def test_gap_1_gives_25(self):
        assert calculate_gap_score(1) == 25.0

    def test_gap_3_gives_75(self):
        assert calculate_gap_score(3) == 75.0

    def test_divisor_is_four(self):
        """The divisor 4 is derived from scale max–min = 5–1 = 4 (LOGIC_SPEC §3)."""
        for gap in range(5):
            assert calculate_gap_score(gap) == gap / 4 * 100


# ===========================================================================
# 3. calculate_skill_match  (LOGIC_SPEC §4)
# ===========================================================================

class TestCalculateSkillMatch:
    def test_full_match_when_equal(self):
        """Excel: current=4, required=4 → 100%  (LOGIC_SPEC §8)"""
        assert calculate_skill_match(current_level=4, required_level=4) == 100.0

    def test_partial_match_sql(self):
        """SQL: current=1, required=3 → 33.33%  (LOGIC_SPEC §4 and §8)"""
        result = calculate_skill_match(current_level=1, required_level=3)
        assert abs(result - 33.333) < 0.01

    def test_partial_match_75(self):
        """Statistics: current=3, required=4 → 75%  (LOGIC_SPEC §4)"""
        assert calculate_skill_match(current_level=3, required_level=4) == 75.0

    def test_capped_at_100(self):
        """Exceeding the requirement must NOT push match above 100% (LOGIC_SPEC §4)."""
        assert calculate_skill_match(current_level=5, required_level=3) == 100.0

    def test_required_zero_guard(self):
        """If required_level is 0, skill is not needed → 100% match."""
        assert calculate_skill_match(current_level=0, required_level=0) == 100.0

    def test_zero_current_level(self):
        """A user who has never touched the skill → 0% match."""
        assert calculate_skill_match(current_level=0, required_level=3) == 0.0

    def test_all_logic_spec_skill_matches(self, logic_spec_career_reqs, logic_spec_user_skills):
        """
        Verify all §8 skill matches used in the career fit calculation.
        SQL=33.3%, Power BI=33.3%, Statistics=100%, Excel=100%, Communication=100%
        """
        expected = {
            _SQL:      33.333,
            _POWER_BI: 33.333,
            _STATS:    100.0,
            _EXCEL:    100.0,
            _COMM:     100.0,
        }
        for sid, exp_match in expected.items():
            req = logic_spec_career_reqs[sid]["required_level"]
            cur = logic_spec_user_skills[sid]
            result = calculate_skill_match(cur, req)
            assert abs(result - exp_match) < 0.1, f"skill_id={sid}: got {result}, expected {exp_match}"


# ===========================================================================
# 4. calculate_career_fit  (LOGIC_SPEC §4)
# ===========================================================================

class TestCalculateCareerFit:
    def test_logic_spec_example(self, logic_spec_career_reqs, logic_spec_user_skills):
        """
        LOGIC_SPEC §8 states Career Fit ≈ 72.6% for this user/career combination.

        Manual verification:
          SQL:       33.33 × 95 = 3,166.7
          Power BI:  33.33 × 80 = 2,666.7
          Statistics:100   × 75 = 7,500.0
          Excel:     100   × 90 = 9,000.0
          Comm:      100   × 85 = 8,500.0
          ─────────────────────────────────
          Σ(match×imp) = 30,833.4
          Σ(imp)       = 425
          CareerFit    = 30,833.4 / 425 = 72.55% ≈ 72.6%
        """
        result = calculate_career_fit(logic_spec_career_reqs, logic_spec_user_skills)
        assert abs(result - 72.55) < 0.1, f"Expected ~72.55%, got {result:.2f}%"

    def test_perfect_fit(self):
        """A user who meets every requirement exactly → 100%."""
        reqs = {1: {"required_level": 3, "importance": 80}}
        user = {1: 3}
        assert calculate_career_fit(reqs, user) == 100.0

    def test_exceeding_requirement_capped(self):
        """Exceeding the requirement still gives 100%, not more."""
        reqs = {1: {"required_level": 3, "importance": 80}}
        user = {1: 5}
        assert calculate_career_fit(reqs, user) == 100.0

    def test_zero_fit_when_no_skills(self):
        """A user with no relevant skills → 0%."""
        reqs = {1: {"required_level": 3, "importance": 80}}
        user = {}
        assert calculate_career_fit(reqs, user) == 0.0

    def test_empty_requirements(self):
        assert calculate_career_fit({}, {}) == 0.0

    def test_single_skill_partial(self):
        reqs = {1: {"required_level": 4, "importance": 100}}
        user = {1: 2}
        # SkillMatch = 2/4 * 100 = 50%; importance=100 → CareerFit = 50%
        assert calculate_career_fit(reqs, user) == 50.0


# ===========================================================================
# 5. calculate_priority_score  (LOGIC_SPEC §5)
# ===========================================================================

class TestCalculatePriorityScore:
    def test_sql_from_logic_spec(self):
        """
        LOGIC_SPEC §8:
          SQL: GapScore=50, importance=95, demand=90, strategic_value=85
          Expected = 0.3(50) + 0.3(95) + 0.2(90) + 0.2(85)
                   = 15 + 28.5 + 18 + 17 = 78.5
        """
        result = calculate_priority_score(
            gap_score=50, importance=95, market_demand=90, strategic_value=85
        )
        assert abs(result - 78.5) < 0.01, f"Expected 78.5, got {result}"

    def test_power_bi_from_logic_spec(self):
        """
        LOGIC_SPEC §8:
          Power BI: GapScore=50, importance=80, demand=85, strategic_value=70
          Expected = 0.3(50) + 0.3(80) + 0.2(85) + 0.2(70)
                   = 15 + 24 + 17 + 14 = 70.0
        """
        result = calculate_priority_score(
            gap_score=50, importance=80, market_demand=85, strategic_value=70
        )
        assert abs(result - 70.0) < 0.01, f"Expected 70.0, got {result}"

    def test_weights_sum_correctly(self):
        """0.30 + 0.30 + 0.20 + 0.20 = 1.0 → max score = 100 when all inputs = 100."""
        result = calculate_priority_score(100, 100, 100, 100)
        assert result == 100.0

    def test_zero_gap_skill_still_scored(self):
        """A skill with no gap has GapScore=0; priority is driven by the other factors."""
        result = calculate_priority_score(gap_score=0, importance=90, market_demand=75, strategic_value=40)
        expected = 0.30 * 0 + 0.30 * 90 + 0.20 * 75 + 0.20 * 40
        assert abs(result - expected) < 0.01

    def test_sql_higher_than_power_bi(self):
        """SQL must score higher than Power BI (78.5 > 70.0)  — from §8."""
        sql_ps = calculate_priority_score(50, 95, 90, 85)
        pbi_ps = calculate_priority_score(50, 80, 85, 70)
        assert sql_ps > pbi_ps


# ===========================================================================
# 6. get_learning_candidates  (LOGIC_SPEC §6 Step 1–2)
# ===========================================================================

class TestGetLearningCandidates:
    def test_only_gap_skills_are_candidates(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
    ):
        """
        From §8: only SQL and Power BI have gaps.
        Statistics, Excel, Communication have gap=0 and must NOT appear.
        """
        candidates = get_learning_candidates(
            logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
        )
        names = [c["skill_name"] for c in candidates]
        assert "SQL" in names
        assert "Power BI" in names
        assert "Statistics" not in names
        assert "Excel" not in names
        assert "Communication" not in names

    def test_candidates_sorted_by_priority_score_descending(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
    ):
        """SQL (78.5) must appear before Power BI (70.0)."""
        candidates = get_learning_candidates(
            logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
        )
        assert candidates[0]["skill_name"] == "SQL"
        assert candidates[1]["skill_name"] == "Power BI"

    def test_candidate_gap_scores(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
    ):
        """Both SQL and Power BI have gap=2 → gap_score=50 (§3)."""
        candidates = get_learning_candidates(
            logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
        )
        for c in candidates:
            assert c["gap"] == 2
            assert c["gap_score"] == 50.0

    def test_candidate_priority_scores(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
    ):
        """Verify exact priority scores from §8."""
        candidates = get_learning_candidates(
            logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
        )
        by_name = {c["skill_name"]: c for c in candidates}
        assert abs(by_name["SQL"]["priority_score"] - 78.5) < 0.1
        assert abs(by_name["Power BI"]["priority_score"] - 70.0) < 0.1

    def test_returns_empty_when_no_gaps(self):
        """A user who meets all requirements → no candidates."""
        reqs = {1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60}}
        user = {1: 3}
        assert get_learning_candidates(reqs, user) == []

    def test_candidate_has_all_required_fields(
        self, logic_spec_career_reqs, logic_spec_user_skills
    ):
        candidates = get_learning_candidates(logic_spec_career_reqs, logic_spec_user_skills)
        required_fields = {
            "skill_id", "skill_name", "category",
            "current_level", "required_level",
            "gap", "gap_score", "skill_match",
            "importance", "market_demand", "strategic_value",
            "priority_score",
        }
        for c in candidates:
            missing = required_fields - set(c.keys())
            assert not missing, f"Candidate missing fields: {missing}"


# ===========================================================================
# 7. check_prerequisite_block  (LOGIC_SPEC §6 Step 3)
# ===========================================================================

class TestCheckPrerequisiteBlock:
    def test_power_bi_blocked_by_sql(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_prerequisites
    ):
        """
        LOGIC_SPEC §8: SQL required=3, user has SQL=1 → 1 < 3 → Power BI BLOCKED.
        """
        result = check_prerequisite_block(
            _POWER_BI, logic_spec_prerequisites, logic_spec_career_reqs, logic_spec_user_skills
        )
        assert result["is_blocked"] is True
        assert _SQL in result["blocked_by_ids"]

    def test_sql_not_blocked(
        self, logic_spec_career_reqs, logic_spec_user_skills, logic_spec_prerequisites
    ):
        """SQL has no prerequisites → NOT blocked."""
        result = check_prerequisite_block(
            _SQL, logic_spec_prerequisites, logic_spec_career_reqs, logic_spec_user_skills
        )
        assert result["is_blocked"] is False
        assert result["blocked_by_ids"] == []

    def test_power_bi_unblocked_after_sql_met(self, logic_spec_career_reqs, logic_spec_prerequisites):
        """Once the user meets the SQL requirement, Power BI is unblocked."""
        user_met_sql = {_SQL: 3, _POWER_BI: 1}   # SQL now at required level
        result = check_prerequisite_block(
            _POWER_BI, logic_spec_prerequisites, logic_spec_career_reqs, user_met_sql
        )
        assert result["is_blocked"] is False

    def test_prerequisite_not_in_career_is_ignored(self):
        """
        If a prerequisite skill is not required by the target career,
        it should NOT block the dependent skill.
        """
        career_reqs = {
            2: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            # Skill 1 (the prerequisite) is NOT in this career's requirements
        }
        prerequisites = {2: [1]}   # Skill 2 requires Skill 1
        user = {2: 1}              # User hasn't met Skill 2's requirement
        result = check_prerequisite_block(2, prerequisites, career_reqs, user)
        assert result["is_blocked"] is False

    def test_multiple_prerequisites_one_unmet(self):
        """Blocked if ANY prerequisite is unmet."""
        career_reqs = {
            1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            2: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            3: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
        }
        prerequisites = {3: [1, 2]}   # Skill 3 requires both 1 and 2
        user = {1: 3, 2: 1, 3: 1}    # Skill 1 met, Skill 2 not met → Skill 3 blocked
        result = check_prerequisite_block(3, prerequisites, career_reqs, user)
        assert result["is_blocked"] is True
        assert 2 in result["blocked_by_ids"]
        assert 1 not in result["blocked_by_ids"]

    def test_multiple_prerequisites_all_met(self):
        """Unblocked only when ALL prerequisites are met."""
        career_reqs = {
            1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            2: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            3: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
        }
        prerequisites = {3: [1, 2]}
        user = {1: 3, 2: 3, 3: 1}    # Both prerequisites met
        result = check_prerequisite_block(3, prerequisites, career_reqs, user)
        assert result["is_blocked"] is False

    def test_no_prerequisites_never_blocked(self):
        result = check_prerequisite_block(_SQL, {}, {}, {})
        assert result["is_blocked"] is False


# ===========================================================================
# 8. recommend_next_skill  (LOGIC_SPEC §6 Step 4)
# ===========================================================================

class TestRecommendNextSkill:
    def test_recommends_sql_not_power_bi(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        LOGIC_SPEC §8: Both SQL and Power BI have gaps.
        Power BI is blocked by SQL. System must recommend SQL.
        """
        rec = recommend_next_skill(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        assert rec is not None
        assert rec["skill_name"] == "SQL"

    def test_recommendation_is_not_blocked(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """The recommended skill must never be blocked."""
        rec = recommend_next_skill(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        assert rec["is_blocked"] is False

    def test_recommendation_has_explanation_field(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """Every recommendation must carry a structured explanation."""
        rec = recommend_next_skill(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        assert "explanation" in rec

    # --- Explanation components ---

    def test_explanation_gap_contribution(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        SQL: gap_score=50 → gap_contribution = 0.30 × 50 = 15.0
        """
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert abs(rec["explanation"]["gap_contribution"] - 15.0) < 0.01

    def test_explanation_importance_contribution(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        SQL: importance=95 → importance_contribution = 0.30 × 95 = 28.5
        """
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert abs(rec["explanation"]["importance_contribution"] - 28.5) < 0.01

    def test_explanation_demand_contribution(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        SQL: market_demand=90 → demand_contribution = 0.20 × 90 = 18.0
        """
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert abs(rec["explanation"]["demand_contribution"] - 18.0) < 0.01

    def test_explanation_strategic_contribution(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        SQL: strategic_value=85 → strategic_contribution = 0.20 × 85 = 17.0
        """
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert abs(rec["explanation"]["strategic_contribution"] - 17.0) < 0.01

    def test_explanation_contributions_sum_to_priority_score(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """The four contributions must sum to the priority_score."""
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        exp = rec["explanation"]
        total = (
            exp["gap_contribution"]
            + exp["importance_contribution"]
            + exp["demand_contribution"]
            + exp["strategic_contribution"]
        )
        assert abs(total - rec["priority_score"]) < 0.1

    def test_explanation_prerequisite_status_is_string(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """prerequisite_status must be a non-empty human-readable string."""
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        status = rec["explanation"]["prerequisite_status"]
        assert isinstance(status, str) and status.strip()

    def test_explanation_priority_rank_is_one(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """SQL is the #1 unblocked candidate."""
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert rec["explanation"]["priority_rank"] == 1

    def test_explanation_why_recommended_present(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert "why_recommended" in rec["explanation"]
        assert rec["explanation"]["why_recommended"]

    def test_explanation_breakdown_string_present(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert "priority_score_breakdown" in rec["explanation"]

    # --- Priority score accuracy ---

    def test_recommended_priority_score(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """SQL priority score must be ≈ 78.5 (LOGIC_SPEC §8)."""
        rec = recommend_next_skill(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert abs(rec["priority_score"] - 78.5) < 0.1

    # --- Edge cases ---

    def test_returns_none_when_no_gaps(self):
        reqs = {1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60}}
        user = {1: 3}
        assert recommend_next_skill(reqs, user, {}) is None

    def test_returns_none_when_all_blocked(self):
        """If every candidate is blocked, return None."""
        reqs = {
            1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
            2: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60},
        }
        user = {1: 1, 2: 1}
        prerequisites = {2: [1]}    # Power BI blocked by SQL
        # SQL blocked by Power BI (circular — pathological case)
        prerequisites_circular = {1: [2], 2: [1]}
        assert recommend_next_skill(reqs, user, prerequisites_circular) is None

    def test_recommends_power_bi_after_sql_met(
        self,
        logic_spec_career_reqs,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        Once SQL is met (current=3), Power BI becomes unblocked.
        If that is the only remaining gap, Power BI should be recommended.
        """
        user_sql_met = {
            _SQL:      3,   # SQL requirement now met
            _POWER_BI: 1,   # still a gap
            _STATS:    3,
            _EXCEL:    4,
            _COMM:     4,
        }
        rec = recommend_next_skill(
            logic_spec_career_reqs,
            user_sql_met,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        assert rec is not None
        assert rec["skill_name"] == "Power BI"
        assert rec["is_blocked"] is False


# ===========================================================================
# 9. generate_learning_roadmap  (LOGIC_SPEC §7)
# ===========================================================================

class TestGenerateLearningRoadmap:
    def test_sql_before_power_bi(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """
        LOGIC_SPEC §7: prerequisites must be respected in roadmap order.
        SQL → Power BI (SQL must appear first).
        """
        roadmap = generate_learning_roadmap(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        names = [s["skill_name"] for s in roadmap]
        assert names.index("SQL") < names.index("Power BI")

    def test_only_gap_skills_in_roadmap(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """Skills with no gap must NOT appear in the roadmap."""
        roadmap = generate_learning_roadmap(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        names = [s["skill_name"] for s in roadmap]
        assert "Statistics" not in names
        assert "Excel" not in names
        assert "Communication" not in names

    def test_roadmap_contains_all_candidates(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """Both gap skills (SQL and Power BI) must appear in the roadmap."""
        roadmap = generate_learning_roadmap(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        names = [s["skill_name"] for s in roadmap]
        assert "SQL" in names
        assert "Power BI" in names

    def test_empty_roadmap_when_no_gaps(self):
        reqs = {1: {"required_level": 3, "importance": 80, "market_demand": 70, "strategic_value": 60}}
        user = {1: 3}
        assert generate_learning_roadmap(reqs, user, {}) == []

    def test_roadmap_entry_has_required_fields(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        roadmap = generate_learning_roadmap(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        required_fields = {
            "skill_id", "skill_name", "category",
            "current_level", "required_level",
            "gap", "gap_score", "skill_match",
            "importance", "market_demand", "strategic_value",
            "priority_score",
        }
        for entry in roadmap:
            missing = required_fields - set(entry.keys())
            assert not missing, f"Roadmap entry missing fields: {missing}"

    def test_roadmap_length_matches_candidate_count(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """Roadmap length must equal the number of gap skills."""
        roadmap = generate_learning_roadmap(
            logic_spec_career_reqs,
            logic_spec_user_skills,
            logic_spec_prerequisites,
            logic_spec_skills_meta,
        )
        candidates = get_learning_candidates(
            logic_spec_career_reqs, logic_spec_user_skills, logic_spec_skills_meta
        )
        assert len(roadmap) == len(candidates)


# ===========================================================================
# 10. compute_skill_analysis (internal helper used by api.py)
# ===========================================================================

class TestComputeSkillAnalysis:
    def test_includes_all_career_skills(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        """All 5 career skills must appear — including those with no gap."""
        analysis = compute_skill_analysis(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        assert len(analysis) == 5

    def test_is_candidate_flag(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        analysis = compute_skill_analysis(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        by_name = {s["skill_name"]: s for s in analysis}
        assert by_name["SQL"]["is_candidate"] is True
        assert by_name["Power BI"]["is_candidate"] is True
        assert by_name["Statistics"]["is_candidate"] is False
        assert by_name["Excel"]["is_candidate"] is False
        assert by_name["Communication"]["is_candidate"] is False

    def test_power_bi_is_blocked_flag(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        analysis = compute_skill_analysis(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        by_name = {s["skill_name"]: s for s in analysis}
        assert by_name["Power BI"]["is_blocked"] is True
        assert "SQL" in by_name["Power BI"]["blocked_by"]

    def test_sql_is_not_blocked_flag(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        analysis = compute_skill_analysis(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        by_name = {s["skill_name"]: s for s in analysis}
        assert by_name["SQL"]["is_blocked"] is False

    def test_sorted_by_priority_score(
        self,
        logic_spec_career_reqs,
        logic_spec_user_skills,
        logic_spec_prerequisites,
        logic_spec_skills_meta,
    ):
        analysis = compute_skill_analysis(
            logic_spec_career_reqs, logic_spec_user_skills,
            logic_spec_prerequisites, logic_spec_skills_meta,
        )
        scores = [s["priority_score"] for s in analysis]
        assert scores == sorted(scores, reverse=True)
