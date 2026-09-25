"""
api.py
PathWise Flask API server.
Serves the web/ frontend as static files and exposes JSON endpoints.

Run:
    py src/api.py
Then open:
    http://localhost:5000
"""

import os
import sys

# Allow importing engine and data_loader from same src/ directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory

import data_loader as dl
import engine as eng

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WEB = os.path.join(_ROOT, "web")

app = Flask(__name__, static_folder=_WEB, static_url_path="")

# Load all static data once at startup
_skills = dl.load_skills()
_careers = dl.load_careers()
_career_reqs = dl.load_career_requirements()
_prerequisites = dl.load_prerequisites()


def _load_user():
    """Load demo user skills fresh from disk on each request (supports live edits)."""
    return dl.load_user_skills()


# ---------------------------------------------------------------------------
# Static file serving (serves the web/ directory)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(_WEB, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(_WEB, filename)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.route("/api/skills", methods=["GET"])
def api_skills():
    """Return all skills."""
    payload = [
        {"skill_id": sid, **meta}
        for sid, meta in _skills.items()
    ]
    return jsonify(payload)


@app.route("/api/careers", methods=["GET"])
def api_careers():
    """Return all careers."""
    payload = [
        {"career_id": cid, **meta}
        for cid, meta in _careers.items()
    ]
    return jsonify(payload)


@app.route("/api/user/skills", methods=["GET"])
def api_get_user_skills():
    """Return demo user's current skill levels."""
    user = _load_user()
    payload = [
        {
            "skill_id": sid,
            "skill_name": _skills.get(sid, {}).get("skill_name", str(sid)),
            "category": _skills.get(sid, {}).get("category", ""),
            "current_level": level,
        }
        for sid, level in user.items()
    ]
    # Sort by category then skill_name
    payload.sort(key=lambda x: (x["category"], x["skill_name"]))
    return jsonify(payload)


@app.route("/api/user/skills", methods=["POST"])
def api_update_user_skill():
    """
    Update a single skill level for the demo user.
    Body: {"skill_id": int, "current_level": int}
    """
    data = request.get_json()
    if not data or "skill_id" not in data or "current_level" not in data:
        return jsonify({"error": "skill_id and current_level are required"}), 400

    skill_id = int(data["skill_id"])
    level = int(data["current_level"])

    if level < 1 or level > 5:
        return jsonify({"error": "current_level must be between 1 and 5"}), 400

    if skill_id not in _skills:
        return jsonify({"error": f"Unknown skill_id: {skill_id}"}), 404

    user = _load_user()
    user[skill_id] = level
    dl.save_user_skills(user)
    return jsonify({"ok": True, "skill_id": skill_id, "current_level": level})


@app.route("/api/analysis", methods=["GET"])
def api_analysis():
    """
    Full skill gap analysis for a given career.
    Query param: career_id (int, required)
    Returns: career_fit, recommendation, skill_analysis list
    """
    career_id = request.args.get("career_id", type=int)
    if career_id is None:
        return jsonify({"error": "career_id query param is required"}), 400

    if career_id not in _careers:
        return jsonify({"error": f"Unknown career_id: {career_id}"}), 404

    career_reqs = _career_reqs.get(career_id, {})
    user = _load_user()

    career_fit = eng.calculate_career_fit(career_reqs, user)
    skill_analysis = eng.compute_skill_analysis(career_reqs, user, _prerequisites, _skills)
    recommendation = eng.recommend_next_skill(career_reqs, user, _prerequisites, _skills)

    return jsonify({
        "career_id": career_id,
        "career_name": _careers[career_id]["career_name"],
        "career_fit": round(career_fit, 2),
        "recommendation": recommendation,
        "skill_analysis": skill_analysis,
    })


@app.route("/api/roadmap", methods=["GET"])
def api_roadmap():
    """
    Prerequisite-ordered learning roadmap for a given career.
    Query param: career_id (int, required)
    """
    career_id = request.args.get("career_id", type=int)
    if career_id is None:
        return jsonify({"error": "career_id query param is required"}), 400

    if career_id not in _careers:
        return jsonify({"error": f"Unknown career_id: {career_id}"}), 404

    career_reqs = _career_reqs.get(career_id, {})
    user = _load_user()

    roadmap = eng.generate_learning_roadmap(career_reqs, user, _prerequisites, _skills)

    return jsonify({
        "career_id": career_id,
        "career_name": _careers[career_id]["career_name"],
        "roadmap": roadmap,
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"PathWise API starting on http://localhost:5000")
    print(f"Serving web UI from: {_WEB}")
    app.run(debug=True, port=5000)
