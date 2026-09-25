"""
validate_data.py
Validates all PathWise CSV files against their expected schema.

Can be run directly:
    py src/validate_data.py

Returns exit code 0 if all files pass, exit code 1 if any error is found.

Design:
- Each validate_* function accepts raw CSV rows (list of dicts from csv.DictReader)
  plus any reference sets needed for cross-file checks.
- This makes every rule unit-testable with injected data — no file I/O in the
  validation logic itself.
- validate_all() is the only function that touches the filesystem.
"""

from __future__ import annotations

import csv
import os
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Schema definitions (source of truth for column names)
# ---------------------------------------------------------------------------

# Expected columns for each CSV file (order does not matter)
EXPECTED_COLUMNS: dict[str, list[str]] = {
    "skills.csv": ["skill_id", "skill_name", "category"],
    "careers.csv": ["career_id", "career_name"],
    "career_requirements.csv": [
        "career_id", "skill_id", "required_level",
        "importance", "market_demand", "strategic_value",
    ],
    "prerequisites.csv": ["skill_id", "prerequisite_skill_id"],
    "demo_user_skills.csv": ["skill_id", "current_level"],
}

VALID_CATEGORIES = {"Technical", "Business", "Soft Skill"}

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _is_int(value: str) -> bool:
    """Return True if value is a non-empty string representing an integer."""
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def _check_columns(filename: str, actual_columns: list[str]) -> list[str]:
    """
    Compare actual CSV header columns against the expected schema.
    Returns a list of error strings (empty list = OK).
    """
    errors: list[str] = []
    expected = set(EXPECTED_COLUMNS.get(filename, []))
    actual = set(actual_columns)

    missing = expected - actual
    extra = actual - expected

    for col in sorted(missing):
        errors.append(f"{filename}: missing required column '{col}'")
    for col in sorted(extra):
        errors.append(f"{filename}: unexpected column '{col}' (not in schema)")

    return errors


# ---------------------------------------------------------------------------
# Per-file validation functions
# All accept a list of raw row dicts (values are strings, as from csv.DictReader).
# ---------------------------------------------------------------------------

def validate_skills(rows: list[dict]) -> list[str]:
    """
    Validates skills.csv rows.
    Checks: required columns, no missing values, integer skill_id > 0,
            no duplicate skill_ids, non-empty skill_name, valid category.
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, row in enumerate(rows, start=2):   # row 1 = header
        sid_raw = row.get("skill_id", "").strip()
        name = row.get("skill_name", "").strip()
        category = row.get("category", "").strip()

        # Missing values
        for field, val in [("skill_id", sid_raw), ("skill_name", name), ("category", category)]:
            if not val:
                errors.append(f"skills.csv row {i}: '{field}' is empty")

        # skill_id must be a positive integer
        if sid_raw and not _is_int(sid_raw):
            errors.append(f"skills.csv row {i}: skill_id '{sid_raw}' is not an integer")
        elif sid_raw and _is_int(sid_raw) and int(sid_raw) <= 0:
            errors.append(f"skills.csv row {i}: skill_id '{sid_raw}' must be > 0")

        # Duplicate skill_id
        if sid_raw and _is_int(sid_raw):
            if sid_raw in seen_ids:
                errors.append(f"skills.csv row {i}: duplicate skill_id '{sid_raw}'")
            seen_ids.add(sid_raw)

        # Valid category
        if category and category not in VALID_CATEGORIES:
            errors.append(
                f"skills.csv row {i}: category '{category}' is not valid "
                f"(expected one of: {sorted(VALID_CATEGORIES)})"
            )

    return errors


def validate_careers(rows: list[dict]) -> list[str]:
    """
    Validates careers.csv rows.
    Checks: required columns, no missing values, integer career_id > 0,
            no duplicate career_ids, non-empty career_name.
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, row in enumerate(rows, start=2):
        cid_raw = row.get("career_id", "").strip()
        name = row.get("career_name", "").strip()

        for field, val in [("career_id", cid_raw), ("career_name", name)]:
            if not val:
                errors.append(f"careers.csv row {i}: '{field}' is empty")

        if cid_raw and not _is_int(cid_raw):
            errors.append(f"careers.csv row {i}: career_id '{cid_raw}' is not an integer")
        elif cid_raw and _is_int(cid_raw) and int(cid_raw) <= 0:
            errors.append(f"careers.csv row {i}: career_id '{cid_raw}' must be > 0")

        if cid_raw and _is_int(cid_raw):
            if cid_raw in seen_ids:
                errors.append(f"careers.csv row {i}: duplicate career_id '{cid_raw}'")
            seen_ids.add(cid_raw)

    return errors


def validate_career_requirements(
    rows: list[dict],
    valid_skill_ids: set[int],
    valid_career_ids: set[int],
) -> list[str]:
    """
    Validates career_requirements.csv rows.
    Checks: required columns, no missing values, integer types,
            career_id in valid_career_ids, skill_id in valid_skill_ids,
            no duplicate (career_id, skill_id) pairs,
            required_level in [1, 5],
            importance / market_demand / strategic_value in [0, 100].
    """
    errors: list[str] = []
    seen_pairs: set[tuple] = set()

    int_fields = ["career_id", "skill_id", "required_level", "importance", "market_demand", "strategic_value"]

    for i, row in enumerate(rows, start=2):
        # Missing values
        for field in int_fields:
            if not row.get(field, "").strip():
                errors.append(f"career_requirements.csv row {i}: '{field}' is empty")

        # All fields must be integers
        parsed: dict[str, int] = {}
        all_ok = True
        for field in int_fields:
            raw = row.get(field, "").strip()
            if raw and not _is_int(raw):
                errors.append(
                    f"career_requirements.csv row {i}: '{field}' value '{raw}' is not an integer"
                )
                all_ok = False
            elif raw:
                parsed[field] = int(raw)

        if not all_ok:
            continue   # Skip cross-checks if we can't parse the row

        cid = parsed.get("career_id")
        sid = parsed.get("skill_id")
        req = parsed.get("required_level")
        imp = parsed.get("importance")
        dem = parsed.get("market_demand")
        strat = parsed.get("strategic_value")

        # Foreign key: career_id
        if cid is not None and cid not in valid_career_ids:
            errors.append(
                f"career_requirements.csv row {i}: career_id {cid} "
                f"does not exist in careers.csv"
            )

        # Foreign key: skill_id
        if sid is not None and sid not in valid_skill_ids:
            errors.append(
                f"career_requirements.csv row {i}: skill_id {sid} "
                f"does not exist in skills.csv"
            )

        # Duplicate (career_id, skill_id)
        if cid is not None and sid is not None:
            pair = (cid, sid)
            if pair in seen_pairs:
                errors.append(
                    f"career_requirements.csv row {i}: duplicate (career_id={cid}, skill_id={sid}) pair"
                )
            seen_pairs.add(pair)

        # required_level: 1–5
        if req is not None and not (1 <= req <= 5):
            errors.append(
                f"career_requirements.csv row {i}: required_level {req} "
                f"is out of range (must be 1–5)"
            )

        # importance, market_demand, strategic_value: 0–100
        for field_name, val in [("importance", imp), ("market_demand", dem), ("strategic_value", strat)]:
            if val is not None and not (0 <= val <= 100):
                errors.append(
                    f"career_requirements.csv row {i}: {field_name} {val} "
                    f"is out of range (must be 0–100)"
                )

    return errors


def validate_prerequisites(
    rows: list[dict],
    valid_skill_ids: set[int],
) -> list[str]:
    """
    Validates prerequisites.csv rows.
    Checks: required columns, no missing values, integer types,
            both skill_id and prerequisite_skill_id in valid_skill_ids,
            no self-references (skill cannot be its own prerequisite),
            no duplicate (skill_id, prerequisite_skill_id) pairs.
    """
    errors: list[str] = []
    seen_pairs: set[tuple] = set()

    for i, row in enumerate(rows, start=2):
        sid_raw = row.get("skill_id", "").strip()
        prereq_raw = row.get("prerequisite_skill_id", "").strip()

        for field, val in [("skill_id", sid_raw), ("prerequisite_skill_id", prereq_raw)]:
            if not val:
                errors.append(f"prerequisites.csv row {i}: '{field}' is empty")

        sid_ok = sid_raw and _is_int(sid_raw)
        prereq_ok = prereq_raw and _is_int(prereq_raw)

        if sid_raw and not sid_ok:
            errors.append(f"prerequisites.csv row {i}: skill_id '{sid_raw}' is not an integer")
        if prereq_raw and not prereq_ok:
            errors.append(f"prerequisites.csv row {i}: prerequisite_skill_id '{prereq_raw}' is not an integer")

        if not (sid_ok and prereq_ok):
            continue

        sid = int(sid_raw)
        prereq = int(prereq_raw)

        # Self-reference
        if sid == prereq:
            errors.append(
                f"prerequisites.csv row {i}: skill_id {sid} lists itself as a prerequisite"
            )

        # Foreign keys
        if sid not in valid_skill_ids:
            errors.append(
                f"prerequisites.csv row {i}: skill_id {sid} does not exist in skills.csv"
            )
        if prereq not in valid_skill_ids:
            errors.append(
                f"prerequisites.csv row {i}: prerequisite_skill_id {prereq} "
                f"does not exist in skills.csv"
            )

        # Duplicate pair
        pair = (sid, prereq)
        if pair in seen_pairs:
            errors.append(
                f"prerequisites.csv row {i}: duplicate (skill_id={sid}, "
                f"prerequisite_skill_id={prereq}) pair"
            )
        seen_pairs.add(pair)

    return errors


def validate_user_skills(
    rows: list[dict],
    valid_skill_ids: set[int],
) -> list[str]:
    """
    Validates demo_user_skills.csv rows.
    Checks: required columns, no missing values, integer types,
            skill_id in valid_skill_ids, no duplicate skill_ids,
            current_level in [1, 5].
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, row in enumerate(rows, start=2):
        sid_raw = row.get("skill_id", "").strip()
        level_raw = row.get("current_level", "").strip()

        for field, val in [("skill_id", sid_raw), ("current_level", level_raw)]:
            if not val:
                errors.append(f"demo_user_skills.csv row {i}: '{field}' is empty")

        sid_ok = sid_raw and _is_int(sid_raw)
        level_ok = level_raw and _is_int(level_raw)

        if sid_raw and not sid_ok:
            errors.append(f"demo_user_skills.csv row {i}: skill_id '{sid_raw}' is not an integer")
        if level_raw and not level_ok:
            errors.append(
                f"demo_user_skills.csv row {i}: current_level '{level_raw}' is not an integer"
            )

        # Duplicate skill_id
        if sid_ok:
            if sid_raw in seen_ids:
                errors.append(f"demo_user_skills.csv row {i}: duplicate skill_id '{sid_raw}'")
            seen_ids.add(sid_raw)

        # Foreign key: skill_id
        if sid_ok and int(sid_raw) not in valid_skill_ids:
            errors.append(
                f"demo_user_skills.csv row {i}: skill_id {sid_raw} "
                f"does not exist in skills.csv"
            )

        # current_level: 1–5
        if level_ok:
            level = int(level_raw)
            if not (1 <= level <= 5):
                errors.append(
                    f"demo_user_skills.csv row {i}: current_level {level} "
                    f"is out of range (must be 1–5)"
                )

    return errors


# ---------------------------------------------------------------------------
# Master validator
# ---------------------------------------------------------------------------

def validate_all(data_dir: str | None = None) -> list[str]:
    """
    Loads all CSV files from data_dir (defaults to the project data/ directory)
    and runs every validation check.

    Returns a list of error strings.  An empty list means all files are valid.
    """
    if data_dir is None:
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(_root, "data")

    all_errors: list[str] = []

    def _read(filename: str) -> tuple[list[str], list[dict]]:
        """Read CSV, return (columns, rows). Returns ([], []) if file missing."""
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            all_errors.append(f"{filename}: file not found at {path}")
            return [], []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            columns = list(reader.fieldnames or [])
        return columns, rows

    # --- skills.csv ---
    cols, skills_rows = _read("skills.csv")
    if cols:
        all_errors.extend(_check_columns("skills.csv", cols))
        all_errors.extend(validate_skills(skills_rows))

    # Build valid skill ID set for cross-file checks
    valid_skill_ids: set[int] = set()
    for row in skills_rows:
        raw = row.get("skill_id", "").strip()
        if _is_int(raw):
            valid_skill_ids.add(int(raw))

    # --- careers.csv ---
    cols, careers_rows = _read("careers.csv")
    if cols:
        all_errors.extend(_check_columns("careers.csv", cols))
        all_errors.extend(validate_careers(careers_rows))

    valid_career_ids: set[int] = set()
    for row in careers_rows:
        raw = row.get("career_id", "").strip()
        if _is_int(raw):
            valid_career_ids.add(int(raw))

    # --- career_requirements.csv ---
    cols, reqs_rows = _read("career_requirements.csv")
    if cols:
        all_errors.extend(_check_columns("career_requirements.csv", cols))
        all_errors.extend(validate_career_requirements(reqs_rows, valid_skill_ids, valid_career_ids))

    # --- prerequisites.csv ---
    cols, prereq_rows = _read("prerequisites.csv")
    if cols:
        all_errors.extend(_check_columns("prerequisites.csv", cols))
        all_errors.extend(validate_prerequisites(prereq_rows, valid_skill_ids))

    # --- demo_user_skills.csv ---
    cols, user_rows = _read("demo_user_skills.csv")
    if cols:
        all_errors.extend(_check_columns("demo_user_skills.csv", cols))
        all_errors.extend(validate_user_skills(user_rows, valid_skill_ids))

    return all_errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _print_report(errors: list[str]) -> None:
    divider = "-" * 60
    print(divider)
    print("PathWise - Data Validation Report")
    print(divider)
    if not errors:
        print("OK  All files valid. No errors found.")
    else:
        print(f"FAIL  {len(errors)} error(s) found:\n")
        for n, err in enumerate(errors, 1):
            print(f"  [{n}] {err}")
    print(divider)


if __name__ == "__main__":
    errors = validate_all()
    _print_report(errors)
    sys.exit(0 if not errors else 1)
