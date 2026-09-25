"""
data_loader.py
Reads PathWise CSV files and returns Python dicts/lists.
All paths are resolved relative to the project root (one level up from src/).
"""

import csv
import os

# Project root = parent of the directory containing this file
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_ROOT, "data")


def _csv_path(filename: str) -> str:
    return os.path.join(_DATA, filename)


def load_skills() -> dict:
    """
    Returns {skill_id (int): {"skill_name": str, "category": str}}
    """
    skills = {}
    with open(_csv_path("skills.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = int(row["skill_id"])
            skills[sid] = {
                "skill_name": row["skill_name"],
                "category": row["category"],
            }
    return skills


def load_careers() -> dict:
    """
    Returns {career_id (int): {"career_name": str}}
    """
    careers = {}
    with open(_csv_path("careers.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = int(row["career_id"])
            careers[cid] = {"career_name": row["career_name"]}
    return careers


def load_career_requirements() -> dict:
    """
    Returns {career_id (int): {skill_id (int): {
        "required_level": int,
        "importance": int,
        "market_demand": int,
        "strategic_value": int,
    }}}
    """
    reqs = {}
    with open(_csv_path("career_requirements.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = int(row["career_id"])
            sid = int(row["skill_id"])
            reqs.setdefault(cid, {})[sid] = {
                "required_level": int(row["required_level"]),
                "importance": int(row["importance"]),
                "market_demand": int(row["market_demand"]),
                "strategic_value": int(row["strategic_value"]),
            }
    return reqs


def load_prerequisites() -> dict:
    """
    Returns {skill_id (int): [prerequisite_skill_id (int), ...]}
    A skill may have multiple prerequisites (e.g. Machine Learning requires both Python and Statistics).
    """
    prereqs: dict = {}
    with open(_csv_path("prerequisites.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = int(row["skill_id"])
            prereq = int(row["prerequisite_skill_id"])
            prereqs.setdefault(sid, []).append(prereq)
    return prereqs


def load_user_skills(filename: str = "demo_user_skills.csv") -> dict:
    """
    Returns {skill_id (int): current_level (int)}
    Default file is the demo user. A different filename can be passed for testing.
    """
    user_skills = {}
    with open(_csv_path(filename), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = int(row["skill_id"])
            user_skills[sid] = int(row["current_level"])
    return user_skills


def save_user_skills(user_skills: dict, filename: str = "demo_user_skills.csv") -> None:
    """
    Persists {skill_id: current_level} back to the CSV.
    """
    path = _csv_path(filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["skill_id", "current_level"])
        writer.writeheader()
        for sid, level in sorted(user_skills.items()):
            writer.writerow({"skill_id": sid, "current_level": level})
