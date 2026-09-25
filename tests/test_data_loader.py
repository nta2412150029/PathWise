"""
test_data_loader.py
Tests that every CSV file loads correctly and returns the expected shape.
These tests use the real CSV files in data/ as the source of truth.
Run with:  py -m pytest tests/test_data_loader.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import data_loader as dl


class TestLoadSkills:
    def setup_method(self):
        self.skills = dl.load_skills()

    def test_returns_dict(self):
        assert isinstance(self.skills, dict)

    def test_has_expected_count(self):
        """skills.csv currently defines 20 skills."""
        assert len(self.skills) == 20

    def test_keys_are_ints(self):
        for k in self.skills:
            assert isinstance(k, int)

    def test_each_skill_has_required_fields(self):
        for sid, meta in self.skills.items():
            assert "skill_name" in meta, f"skill_id {sid} missing skill_name"
            assert "category" in meta, f"skill_id {sid} missing category"

    def test_skill_names_are_nonempty_strings(self):
        for sid, meta in self.skills.items():
            assert isinstance(meta["skill_name"], str) and meta["skill_name"].strip(), \
                f"skill_id {sid} has empty skill_name"

    def test_known_skill_exists(self):
        """Skill 1 must be SQL."""
        assert self.skills[1]["skill_name"] == "SQL"

    def test_categories_are_valid(self):
        valid = {"Technical", "Business", "Soft Skill"}
        for sid, meta in self.skills.items():
            assert meta["category"] in valid, \
                f"skill_id {sid} has unexpected category: {meta['category']!r}"


class TestLoadCareers:
    def setup_method(self):
        self.careers = dl.load_careers()

    def test_returns_dict(self):
        assert isinstance(self.careers, dict)

    def test_has_four_careers(self):
        assert len(self.careers) == 4

    def test_keys_are_ints(self):
        for k in self.careers:
            assert isinstance(k, int)

    def test_each_career_has_name(self):
        for cid, meta in self.careers.items():
            assert "career_name" in meta
            assert isinstance(meta["career_name"], str) and meta["career_name"].strip()

    def test_known_careers_present(self):
        names = {meta["career_name"] for meta in self.careers.values()}
        for expected in ["Business Analyst", "Data Analyst", "Marketing Analyst", "Financial Analyst"]:
            assert expected in names, f"{expected!r} not found in careers"


class TestLoadCareerRequirements:
    def setup_method(self):
        self.reqs = dl.load_career_requirements()

    def test_returns_nested_dict(self):
        assert isinstance(self.reqs, dict)
        for career_id, skills in self.reqs.items():
            assert isinstance(career_id, int)
            assert isinstance(skills, dict)

    def test_all_four_careers_present(self):
        assert set(self.reqs.keys()) == {1, 2, 3, 4}

    def test_has_40_total_rows(self):
        total = sum(len(v) for v in self.reqs.values())
        assert total == 40

    def test_required_fields_present(self):
        for cid, skills in self.reqs.items():
            for sid, row in skills.items():
                for field in ("required_level", "importance", "market_demand", "strategic_value"):
                    assert field in row, f"career {cid} skill {sid} missing {field!r}"

    def test_required_level_range(self):
        """required_level must be 1–5."""
        for cid, skills in self.reqs.items():
            for sid, row in skills.items():
                assert 1 <= row["required_level"] <= 5, \
                    f"career {cid} skill {sid} required_level out of range: {row['required_level']}"

    def test_importance_range(self):
        """importance must be 0–100."""
        for cid, skills in self.reqs.items():
            for sid, row in skills.items():
                assert 0 <= row["importance"] <= 100, \
                    f"career {cid} skill {sid} importance out of range: {row['importance']}"

    def test_market_demand_range(self):
        for cid, skills in self.reqs.items():
            for sid, row in skills.items():
                assert 0 <= row["market_demand"] <= 100

    def test_strategic_value_range(self):
        for cid, skills in self.reqs.items():
            for sid, row in skills.items():
                assert 0 <= row["strategic_value"] <= 100

    def test_skill_ids_are_ints(self):
        for cid, skills in self.reqs.items():
            for sid in skills:
                assert isinstance(sid, int)


class TestLoadPrerequisites:
    def setup_method(self):
        self.prereqs = dl.load_prerequisites()

    def test_returns_dict(self):
        assert isinstance(self.prereqs, dict)

    def test_has_six_rules(self):
        """prerequisites.csv defines 6 prerequisite pairs."""
        total = sum(len(v) for v in self.prereqs.values())
        assert total == 6

    def test_keys_and_values_are_ints(self):
        for sid, prereq_list in self.prereqs.items():
            assert isinstance(sid, int)
            for p in prereq_list:
                assert isinstance(p, int)

    def test_power_bi_requires_sql(self):
        """Skill 3 (Power BI) must require skill 1 (SQL)."""
        assert 1 in self.prereqs.get(3, [])

    def test_no_self_reference(self):
        for sid, prereq_list in self.prereqs.items():
            assert sid not in prereq_list, f"skill {sid} lists itself as a prerequisite"


class TestLoadUserSkills:
    def setup_method(self):
        self.user = dl.load_user_skills()

    def test_returns_dict(self):
        assert isinstance(self.user, dict)

    def test_has_20_skills(self):
        assert len(self.user) == 20

    def test_keys_are_ints(self):
        for k in self.user:
            assert isinstance(k, int)

    def test_levels_are_1_to_5(self):
        for sid, level in self.user.items():
            assert 1 <= level <= 5, f"skill {sid} has invalid level: {level}"

    def test_demo_user_known_values(self):
        """Spot-check: Excel (skill 2) = 4, SQL (skill 1) = 1."""
        assert self.user[1] == 1   # SQL: beginner
        assert self.user[2] == 4   # Excel: advanced
        assert self.user[16] == 4  # Communication: advanced


class TestDataConsistency:
    """Cross-file referential integrity checks."""

    def test_career_requirement_skill_ids_exist_in_skills(self):
        skills = dl.load_skills()
        reqs = dl.load_career_requirements()
        for cid, skill_map in reqs.items():
            for sid in skill_map:
                assert sid in skills, \
                    f"career_requirements references skill_id {sid} not in skills.csv"

    def test_prerequisite_skill_ids_exist_in_skills(self):
        skills = dl.load_skills()
        prereqs = dl.load_prerequisites()
        for sid, prereq_list in prereqs.items():
            assert sid in skills, f"prerequisites references unknown skill_id {sid}"
            for p in prereq_list:
                assert p in skills, f"prerequisites references unknown prerequisite_skill_id {p}"

    def test_user_skill_ids_exist_in_skills(self):
        skills = dl.load_skills()
        user = dl.load_user_skills()
        for sid in user:
            assert sid in skills, \
                f"demo_user_skills references skill_id {sid} not in skills.csv"

    def test_career_requirement_career_ids_exist_in_careers(self):
        careers = dl.load_careers()
        reqs = dl.load_career_requirements()
        for cid in reqs:
            assert cid in careers, \
                f"career_requirements references career_id {cid} not in careers.csv"
