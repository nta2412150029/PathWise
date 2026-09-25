"""
test_validate_data.py
Unit tests for src/validate_data.py.

Each test class covers one validation function.
Bad data is injected directly as lists of dicts — no file I/O required.
One integration class (TestRealData) runs validate_all() against the live CSV files.

Run with:  py -m pytest tests/test_validate_data.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import validate_data as vd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Full set of valid skill IDs (matches skills.csv)
VALID_SKILL_IDS = set(range(1, 21))       # 1–20
VALID_CAREER_IDS = {1, 2, 3, 4}


def _has_error_containing(errors: list[str], *fragments: str) -> bool:
    """Return True if any error string contains all given fragments (case-sensitive)."""
    for err in errors:
        if all(f in err for f in fragments):
            return True
    return False


# ---------------------------------------------------------------------------
# _check_columns
# ---------------------------------------------------------------------------

class TestCheckColumns:
    def test_correct_columns_no_errors(self):
        errors = vd._check_columns("skills.csv", ["skill_id", "skill_name", "category"])
        assert errors == []

    def test_missing_column_detected(self):
        errors = vd._check_columns("skills.csv", ["skill_id", "skill_name"])  # category missing
        assert _has_error_containing(errors, "skills.csv", "missing", "category")

    def test_extra_column_detected(self):
        errors = vd._check_columns("skills.csv", ["skill_id", "skill_name", "category", "notes"])
        assert _has_error_containing(errors, "skills.csv", "unexpected", "notes")

    def test_wrong_column_name_detected(self):
        # "name" instead of "skill_name"
        errors = vd._check_columns("skills.csv", ["skill_id", "name", "category"])
        assert _has_error_containing(errors, "skills.csv", "missing", "skill_name")
        assert _has_error_containing(errors, "skills.csv", "unexpected", "name")

    def test_career_requirements_correct(self):
        cols = ["career_id", "skill_id", "required_level", "importance", "market_demand", "strategic_value"]
        assert vd._check_columns("career_requirements.csv", cols) == []

    def test_prerequisites_correct(self):
        assert vd._check_columns("prerequisites.csv", ["skill_id", "prerequisite_skill_id"]) == []


# ---------------------------------------------------------------------------
# validate_skills
# ---------------------------------------------------------------------------

def _good_skills_rows():
    return [
        {"skill_id": "1", "skill_name": "SQL", "category": "Technical"},
        {"skill_id": "2", "skill_name": "Excel", "category": "Technical"},
    ]


class TestValidateSkills:
    def test_valid_data_no_errors(self):
        assert vd.validate_skills(_good_skills_rows()) == []

    def test_missing_skill_id(self):
        rows = [{"skill_id": "", "skill_name": "SQL", "category": "Technical"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "skill_id", "empty")

    def test_missing_skill_name(self):
        rows = [{"skill_id": "1", "skill_name": "", "category": "Technical"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "skill_name", "empty")

    def test_missing_category(self):
        rows = [{"skill_id": "1", "skill_name": "SQL", "category": ""}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "category", "empty")

    def test_non_integer_skill_id(self):
        rows = [{"skill_id": "abc", "skill_name": "SQL", "category": "Technical"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "skill_id", "not an integer")

    def test_zero_skill_id_invalid(self):
        rows = [{"skill_id": "0", "skill_name": "SQL", "category": "Technical"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "skill_id", "must be > 0")

    def test_negative_skill_id_invalid(self):
        rows = [{"skill_id": "-1", "skill_name": "SQL", "category": "Technical"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "skill_id", "must be > 0")

    def test_duplicate_skill_id(self):
        rows = [
            {"skill_id": "1", "skill_name": "SQL", "category": "Technical"},
            {"skill_id": "1", "skill_name": "Excel", "category": "Technical"},
        ]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "duplicate", "skill_id", "1")

    def test_invalid_category(self):
        rows = [{"skill_id": "1", "skill_name": "SQL", "category": "Unknown"}]
        errors = vd.validate_skills(rows)
        assert _has_error_containing(errors, "category", "Unknown")

    def test_all_valid_categories_accepted(self):
        rows = [
            {"skill_id": "1", "skill_name": "A", "category": "Technical"},
            {"skill_id": "2", "skill_name": "B", "category": "Business"},
            {"skill_id": "3", "skill_name": "C", "category": "Soft Skill"},
        ]
        assert vd.validate_skills(rows) == []


# ---------------------------------------------------------------------------
# validate_careers
# ---------------------------------------------------------------------------

def _good_careers_rows():
    return [
        {"career_id": "1", "career_name": "Business Analyst"},
        {"career_id": "2", "career_name": "Data Analyst"},
    ]


class TestValidateCareers:
    def test_valid_data_no_errors(self):
        assert vd.validate_careers(_good_careers_rows()) == []

    def test_missing_career_id(self):
        rows = [{"career_id": "", "career_name": "Business Analyst"}]
        errors = vd.validate_careers(rows)
        assert _has_error_containing(errors, "career_id", "empty")

    def test_missing_career_name(self):
        rows = [{"career_id": "1", "career_name": ""}]
        errors = vd.validate_careers(rows)
        assert _has_error_containing(errors, "career_name", "empty")

    def test_non_integer_career_id(self):
        rows = [{"career_id": "BA", "career_name": "Business Analyst"}]
        errors = vd.validate_careers(rows)
        assert _has_error_containing(errors, "career_id", "not an integer")

    def test_zero_career_id_invalid(self):
        rows = [{"career_id": "0", "career_name": "Business Analyst"}]
        errors = vd.validate_careers(rows)
        assert _has_error_containing(errors, "career_id", "must be > 0")

    def test_duplicate_career_id(self):
        rows = [
            {"career_id": "1", "career_name": "Business Analyst"},
            {"career_id": "1", "career_name": "Data Analyst"},
        ]
        errors = vd.validate_careers(rows)
        assert _has_error_containing(errors, "duplicate", "career_id", "1")


# ---------------------------------------------------------------------------
# validate_career_requirements
# ---------------------------------------------------------------------------

def _good_reqs_rows():
    return [
        {
            "career_id": "1", "skill_id": "1",
            "required_level": "3",
            "importance": "90", "market_demand": "85", "strategic_value": "80",
        },
        {
            "career_id": "2", "skill_id": "2",
            "required_level": "4",
            "importance": "75", "market_demand": "70", "strategic_value": "60",
        },
    ]


class TestValidateCareerRequirements:
    def test_valid_data_no_errors(self):
        errors = vd.validate_career_requirements(_good_reqs_rows(), VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert errors == []

    def test_missing_career_id(self):
        rows = [{**_good_reqs_rows()[0], "career_id": ""}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "career_id", "empty")

    def test_missing_skill_id(self):
        rows = [{**_good_reqs_rows()[0], "skill_id": ""}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "skill_id", "empty")

    def test_missing_required_level(self):
        rows = [{**_good_reqs_rows()[0], "required_level": ""}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "required_level", "empty")

    def test_non_integer_required_level(self):
        rows = [{**_good_reqs_rows()[0], "required_level": "three"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "required_level", "not an integer")

    def test_required_level_too_low(self):
        rows = [{**_good_reqs_rows()[0], "required_level": "0"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "required_level", "out of range")

    def test_required_level_too_high(self):
        rows = [{**_good_reqs_rows()[0], "required_level": "6"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "required_level", "out of range")

    def test_required_level_boundary_1(self):
        rows = [{**_good_reqs_rows()[0], "required_level": "1"}]
        assert vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS) == []

    def test_required_level_boundary_5(self):
        rows = [{**_good_reqs_rows()[0], "required_level": "5"}]
        assert vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS) == []

    def test_importance_out_of_range_high(self):
        rows = [{**_good_reqs_rows()[0], "importance": "101"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "importance", "out of range")

    def test_importance_out_of_range_negative(self):
        rows = [{**_good_reqs_rows()[0], "importance": "-1"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "importance", "out of range")

    def test_market_demand_out_of_range(self):
        rows = [{**_good_reqs_rows()[0], "market_demand": "105"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "market_demand", "out of range")

    def test_strategic_value_out_of_range(self):
        rows = [{**_good_reqs_rows()[0], "strategic_value": "200"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "strategic_value", "out of range")

    def test_invalid_career_id_reference(self):
        rows = [{**_good_reqs_rows()[0], "career_id": "99"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "career_id", "99", "does not exist")

    def test_invalid_skill_id_reference(self):
        rows = [{**_good_reqs_rows()[0], "skill_id": "999"}]
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "skill_id", "999", "does not exist")

    def test_duplicate_career_skill_pair(self):
        row = _good_reqs_rows()[0]
        rows = [row, row]   # exact duplicate
        errors = vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS)
        assert _has_error_containing(errors, "duplicate")

    def test_zero_values_allowed_for_0_100_fields(self):
        rows = [{**_good_reqs_rows()[0], "importance": "0", "market_demand": "0", "strategic_value": "0"}]
        assert vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS) == []

    def test_boundary_100_allowed(self):
        rows = [{**_good_reqs_rows()[0], "importance": "100", "market_demand": "100", "strategic_value": "100"}]
        assert vd.validate_career_requirements(rows, VALID_SKILL_IDS, VALID_CAREER_IDS) == []


# ---------------------------------------------------------------------------
# validate_prerequisites
# ---------------------------------------------------------------------------

def _good_prereq_rows():
    # Power BI (3) requires SQL (1)
    return [{"skill_id": "3", "prerequisite_skill_id": "1"}]


class TestValidatePrerequisites:
    def test_valid_data_no_errors(self):
        assert vd.validate_prerequisites(_good_prereq_rows(), VALID_SKILL_IDS) == []

    def test_missing_skill_id(self):
        rows = [{"skill_id": "", "prerequisite_skill_id": "1"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "empty")

    def test_missing_prerequisite_skill_id(self):
        rows = [{"skill_id": "3", "prerequisite_skill_id": ""}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "prerequisite_skill_id", "empty")

    def test_non_integer_skill_id(self):
        rows = [{"skill_id": "xyz", "prerequisite_skill_id": "1"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "not an integer")

    def test_non_integer_prerequisite_skill_id(self):
        rows = [{"skill_id": "3", "prerequisite_skill_id": "xyz"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "prerequisite_skill_id", "not an integer")

    def test_self_reference_detected(self):
        rows = [{"skill_id": "3", "prerequisite_skill_id": "3"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "itself")

    def test_unknown_skill_id(self):
        rows = [{"skill_id": "999", "prerequisite_skill_id": "1"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "999", "does not exist")

    def test_unknown_prerequisite_skill_id(self):
        rows = [{"skill_id": "3", "prerequisite_skill_id": "999"}]
        errors = vd.validate_prerequisites(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "prerequisite_skill_id", "999", "does not exist")

    def test_duplicate_pair_detected(self):
        row = {"skill_id": "3", "prerequisite_skill_id": "1"}
        errors = vd.validate_prerequisites([row, row], VALID_SKILL_IDS)
        assert _has_error_containing(errors, "duplicate")

    def test_different_pairs_not_duplicate(self):
        rows = [
            {"skill_id": "3", "prerequisite_skill_id": "1"},   # Power BI → SQL
            {"skill_id": "7", "prerequisite_skill_id": "6"},   # Tableau → Data Viz
        ]
        assert vd.validate_prerequisites(rows, VALID_SKILL_IDS) == []


# ---------------------------------------------------------------------------
# validate_user_skills
# ---------------------------------------------------------------------------

def _good_user_rows():
    return [
        {"skill_id": "1", "current_level": "1"},
        {"skill_id": "2", "current_level": "4"},
    ]


class TestValidateUserSkills:
    def test_valid_data_no_errors(self):
        assert vd.validate_user_skills(_good_user_rows(), VALID_SKILL_IDS) == []

    def test_missing_skill_id(self):
        rows = [{"skill_id": "", "current_level": "3"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "empty")

    def test_missing_current_level(self):
        rows = [{"skill_id": "1", "current_level": ""}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "current_level", "empty")

    def test_non_integer_skill_id(self):
        rows = [{"skill_id": "abc", "current_level": "3"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "not an integer")

    def test_non_integer_current_level(self):
        rows = [{"skill_id": "1", "current_level": "expert"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "current_level", "not an integer")

    def test_current_level_zero_invalid(self):
        rows = [{"skill_id": "1", "current_level": "0"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "current_level", "out of range")

    def test_current_level_6_invalid(self):
        rows = [{"skill_id": "1", "current_level": "6"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "current_level", "out of range")

    def test_current_level_boundary_1(self):
        rows = [{"skill_id": "1", "current_level": "1"}]
        assert vd.validate_user_skills(rows, VALID_SKILL_IDS) == []

    def test_current_level_boundary_5(self):
        rows = [{"skill_id": "1", "current_level": "5"}]
        assert vd.validate_user_skills(rows, VALID_SKILL_IDS) == []

    def test_unknown_skill_id_reference(self):
        rows = [{"skill_id": "999", "current_level": "3"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "skill_id", "999", "does not exist")

    def test_duplicate_skill_id(self):
        rows = [
            {"skill_id": "1", "current_level": "3"},
            {"skill_id": "1", "current_level": "4"},
        ]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "duplicate", "skill_id", "1")

    def test_negative_current_level_invalid(self):
        rows = [{"skill_id": "1", "current_level": "-1"}]
        errors = vd.validate_user_skills(rows, VALID_SKILL_IDS)
        assert _has_error_containing(errors, "current_level", "out of range")


# ---------------------------------------------------------------------------
# Integration test: run validate_all() against the real CSV files
# ---------------------------------------------------------------------------

class TestRealData:
    def test_all_csv_files_are_valid(self):
        """
        validate_all() must return zero errors against the project's live CSV files.
        This test catches any regression introduced by manual edits to the data.
        """
        errors = vd.validate_all()
        assert errors == [], (
            f"Real data validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  {e}" for e in errors)
        )
