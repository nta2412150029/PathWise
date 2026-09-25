"""
engine.py
Core PathWise scoring logic.
All formulas follow LOGIC_SPEC.md exactly. Do NOT alter without explicit approval.

Public API (9 required functions):
  calculate_skill_gap()
  calculate_gap_score()
  calculate_skill_match()
  calculate_career_fit()
  calculate_priority_score()
  get_learning_candidates()
  check_prerequisite_block()
  recommend_next_skill()
  generate_learning_roadmap()

Formulas (from LOGIC_SPEC.md):
  Gap           = max(required_level - current_level, 0)
  GapScore      = Gap / 4 * 100
  SkillMatch    = min(current_level / required_level, 1) * 100
  CareerFit     = sum(SkillMatch * importance) / sum(importance)
  PriorityScore = 0.30*GapScore + 0.30*importance + 0.20*market_demand + 0.20*strategic_value

Recommendation rule (LOGIC_SPEC.md §6):
  1. Only skills with Gap > 0 are learning candidates.
  2. A candidate is BLOCKED if the user has not yet reached the required_level
     for any of its prerequisites (evaluated within the target career's requirements).
  3. Recommend the highest-priority UNBLOCKED candidate.
"""

from __future__ import annotations
from typing import Optional


# ===========================================================================
# 1. Pure formula functions
# ===========================================================================

def calculate_skill_gap(required_level: int, current_level: int) -> int:
    """
    Gap = max(required_level - current_level, 0)

    Negative gaps are treated as zero: a student already above the required
    level has no learning requirement for this skill.

    Args:
        required_level: Level required by the target career (1–5).
        current_level:  User's current proficiency (1–5).

    Returns:
        Non-negative integer gap.
    """
    return max(required_level - current_level, 0)


def calculate_gap_score(gap: int) -> float:
    """
    GapScore = gap / 4 * 100

    Normalises the raw gap (0–4) to a 0–100 scale so it can be combined
    with the other 0–100 inputs in the Priority Score formula.

    The divisor is 4 because the skill scale runs 1–5, so the maximum
    possible gap is 5 - 1 = 4.

    Args:
        gap: Raw skill gap (output of calculate_skill_gap).

    Returns:
        Float in [0, 100].
    """
    return gap / 4 * 100


def calculate_skill_match(current_level: int, required_level: int) -> float:
    """
    SkillMatch = min(current_level / required_level, 1) * 100

    Measures how well the user's current level satisfies the career's
    requirement.  Capped at 100%: exceeding the requirement does not push
    the score above 100%.

    Guard: if required_level is 0 the skill is not required → 100% match.

    Args:
        current_level:  User's current proficiency (1–5).
        required_level: Level required by the target career (1–5).

    Returns:
        Float in [0, 100].
    """
    if required_level == 0:
        return 100.0
    return min(current_level / required_level, 1.0) * 100.0


def calculate_priority_score(
    gap_score: float,
    importance: int,
    market_demand: int,
    strategic_value: int,
) -> float:
    """
    PriorityScore = 0.30*GapScore + 0.30*importance + 0.20*market_demand + 0.20*strategic_value

    Weights (from LOGIC_SPEC.md §5):
      30% — Skill gap (how far the user is from the career requirement)
      30% — Career importance (how critical this skill is for the target career)
      20% — Market demand (how sought-after this skill is in the job market)
      20% — Strategic / prerequisite value (how many other skills this unlocks)

    Args:
        gap_score:       Normalised gap score (0–100, from calculate_gap_score).
        importance:      Career importance weight (0–100).
        market_demand:   Market demand weight (0–100).
        strategic_value: Strategic / prerequisite value (0–100).

    Returns:
        Float in [0, 100].
    """
    return (
        0.30 * gap_score
        + 0.30 * importance
        + 0.20 * market_demand
        + 0.20 * strategic_value
    )


# ===========================================================================
# 2. Career-level analysis
# ===========================================================================

def calculate_career_fit(
    career_reqs: dict,
    user_skills: dict,
) -> float:
    """
    CareerFit = sum(SkillMatch_i * importance_i) / sum(importance_i)

    A weighted average of per-skill match percentages, weighted by career
    importance.  Returns a value in [0, 100].

    Args:
        career_reqs: {skill_id: {required_level, importance, ...}}
        user_skills: {skill_id: current_level}

    Returns:
        Career fit percentage (0–100).  0.0 if no skills are required.
    """
    total_weighted_match = 0.0
    total_importance = 0

    for skill_id, req in career_reqs.items():
        current = user_skills.get(skill_id, 0)
        imp = req["importance"]
        sm = calculate_skill_match(current, req["required_level"])
        total_weighted_match += sm * imp
        total_importance += imp

    if total_importance == 0:
        return 0.0

    return total_weighted_match / total_importance


# ===========================================================================
# 3. Candidate selection
# ===========================================================================

def get_learning_candidates(
    career_reqs: dict,
    user_skills: dict,
    skills_meta: Optional[dict] = None,
) -> list[dict]:
    """
    Return all skills with Gap > 0, sorted by Priority Score (descending).

    Only skills with a positive gap are learning candidates (LOGIC_SPEC §6 Step 1).
    This function does NOT apply prerequisite blocking — that is handled by
    check_prerequisite_block() and recommend_next_skill().

    Args:
        career_reqs:  {skill_id: {required_level, importance, market_demand, strategic_value}}
        user_skills:  {skill_id: current_level}
        skills_meta:  Optional {skill_id: {skill_name, category}}

    Returns:
        List of candidate dicts, each containing:
          skill_id, skill_name, category,
          current_level, required_level,
          gap, gap_score, skill_match,
          importance, market_demand, strategic_value,
          priority_score
    """
    if skills_meta is None:
        skills_meta = {}

    candidates = []

    for skill_id, req in career_reqs.items():
        current = user_skills.get(skill_id, 0)
        req_level = req["required_level"]

        gap = calculate_skill_gap(req_level, current)
        if gap == 0:
            continue   # Not a learning candidate

        gs = calculate_gap_score(gap)
        sm = calculate_skill_match(current, req_level)
        imp = req["importance"]
        demand = req["market_demand"]
        strat = req["strategic_value"]
        ps = calculate_priority_score(gs, imp, demand, strat)

        meta = skills_meta.get(skill_id, {})
        candidates.append({
            "skill_id": skill_id,
            "skill_name": meta.get("skill_name", str(skill_id)),
            "category": meta.get("category", ""),
            "current_level": current,
            "required_level": req_level,
            "gap": gap,
            "gap_score": round(gs, 2),
            "skill_match": round(sm, 2),
            "importance": imp,
            "market_demand": demand,
            "strategic_value": strat,
            "priority_score": round(ps, 2),
        })

    candidates.sort(key=lambda x: x["priority_score"], reverse=True)
    return candidates


# ===========================================================================
# 4. Prerequisite checking
# ===========================================================================

def check_prerequisite_block(
    skill_id: int,
    prerequisites: dict,
    career_reqs: dict,
    user_skills: dict,
) -> dict:
    """
    Determine whether a skill is blocked by an unmet prerequisite.

    A skill B is BLOCKED if:
      - B has at least one prerequisite A that is listed in career_reqs, AND
      - the user's current_level for A is below the career's required_level for A.

    Prerequisites for skills not required by the target career are ignored
    (they cannot block a career-specific learning path).

    Args:
        skill_id:      The skill to evaluate.
        prerequisites: {skill_id: [prereq_skill_id, ...]}
        career_reqs:   {skill_id: {required_level, ...}}
        user_skills:   {skill_id: current_level}

    Returns:
        {
            "is_blocked": bool,
            "blocked_by_ids":   [skill_id, ...],    # IDs of unmet prerequisites
            "blocked_by_names": [str, ...]          # placeholder names (IDs as strings)
        }
        Callers that have skills_meta should resolve IDs to names themselves.
    """
    blocked_by_ids = []

    for prereq_id in prerequisites.get(skill_id, []):
        prereq_req = career_reqs.get(prereq_id)
        if prereq_req is None:
            # Prerequisite not required for this career → not a blocker
            continue
        prereq_current = user_skills.get(prereq_id, 0)
        prereq_required = prereq_req["required_level"]
        if prereq_current < prereq_required:
            blocked_by_ids.append(prereq_id)

    return {
        "is_blocked": len(blocked_by_ids) > 0,
        "blocked_by_ids": blocked_by_ids,
        "blocked_by_names": [str(i) for i in blocked_by_ids],  # resolved by callers
    }


# ===========================================================================
# 5. Recommendation
# ===========================================================================

def recommend_next_skill(
    career_reqs: dict,
    user_skills: dict,
    prerequisites: dict,
    skills_meta: Optional[dict] = None,
) -> Optional[dict]:
    """
    Recommend the single highest-priority skill the user can learn next.

    Algorithm (LOGIC_SPEC.md §6):
      Step 1 — Identify all skills with Gap > 0 (learning candidates).
      Step 2 — Calculate Priority Score for each candidate.
      Step 3 — Block candidates whose prerequisites have not been met.
      Step 4 — Recommend the highest-priority UNBLOCKED candidate.

    The returned dict includes a structured `explanation` field that
    identifies every factor that drove the recommendation:
      - gap_contribution       (0.30 × gap_score)
      - importance_contribution (0.30 × importance)
      - demand_contribution    (0.20 × market_demand)
      - strategic_contribution (0.20 × strategic_value)
      - prerequisite_status    (human-readable string)
      - priority_rank          (position in the unblocked candidate list)

    Args:
        career_reqs:  {skill_id: {required_level, importance, market_demand, strategic_value}}
        user_skills:  {skill_id: current_level}
        prerequisites: {skill_id: [prereq_skill_id, ...]}
        skills_meta:  Optional {skill_id: {skill_name, category}}

    Returns:
        Recommendation dict with full explanation, or None if no candidates exist.
    """
    if skills_meta is None:
        skills_meta = {}

    candidates = get_learning_candidates(career_reqs, user_skills, skills_meta)
    if not candidates:
        return None

    unblocked_rank = 0
    for candidate in candidates:
        sid = candidate["skill_id"]
        block_info = check_prerequisite_block(sid, prerequisites, career_reqs, user_skills)

        # Resolve prerequisite names
        blocked_by_names = [
            skills_meta.get(bid, {}).get("skill_name", str(bid))
            for bid in block_info["blocked_by_ids"]
        ]

        if block_info["is_blocked"]:
            continue

        unblocked_rank += 1

        # Build explanation for why this skill is recommended
        gs = candidate["gap_score"]
        imp = candidate["importance"]
        demand = candidate["market_demand"]
        strat = candidate["strategic_value"]

        gap_contrib = round(0.30 * gs, 2)
        imp_contrib = round(0.30 * imp, 2)
        demand_contrib = round(0.20 * demand, 2)
        strat_contrib = round(0.20 * strat, 2)

        prereq_ids = prerequisites.get(sid, [])
        career_prereq_ids = [p for p in prereq_ids if p in career_reqs]
        if not career_prereq_ids:
            prereq_status = "No prerequisites — available to learn immediately"
        else:
            met_prereqs = [
                skills_meta.get(p, {}).get("skill_name", str(p))
                for p in career_prereq_ids
                if user_skills.get(p, 0) >= career_reqs[p]["required_level"]
            ]
            prereq_status = (
                f"Prerequisites met: {', '.join(met_prereqs)}"
                if met_prereqs
                else "No prerequisites — available to learn immediately"
            )

        return {
            **candidate,
            "is_blocked": False,
            "blocked_by": [],
            "explanation": {
                "gap_contribution": gap_contrib,
                "importance_contribution": imp_contrib,
                "demand_contribution": demand_contrib,
                "strategic_contribution": strat_contrib,
                "priority_score_breakdown": (
                    f"0.30 × {gs} (gap) "
                    f"+ 0.30 × {imp} (importance) "
                    f"+ 0.20 × {demand} (demand) "
                    f"+ 0.20 × {strat} (strategic) "
                    f"= {candidate['priority_score']}"
                ),
                "prerequisite_status": prereq_status,
                "priority_rank": unblocked_rank,
                "why_recommended": (
                    f"Highest-priority unblocked skill "
                    f"(rank #{unblocked_rank} among {len(candidates)} candidates)"
                ),
            },
        }

    # All candidates are blocked
    return None


# ===========================================================================
# 6. Learning roadmap
# ===========================================================================

def generate_learning_roadmap(
    career_reqs: dict,
    user_skills: dict,
    prerequisites: dict,
    skills_meta: Optional[dict] = None,
) -> list[dict]:
    """
    Return all learning candidates ordered so that every prerequisite
    appears before the skill that depends on it.

    Uses Kahn's topological sort on the subgraph of candidate skills.
    Ties at the same topological level are broken by priority_score (descending).

    Skills with no gap are excluded from the roadmap.

    Args:
        career_reqs:   {skill_id: {required_level, importance, market_demand, strategic_value}}
        user_skills:   {skill_id: current_level}
        prerequisites: {skill_id: [prereq_skill_id, ...]}
        skills_meta:   Optional {skill_id: {skill_name, category}}

    Returns:
        List of skill dicts in prerequisite-safe learning order.
        Each entry has the same shape as get_learning_candidates() items.
    """
    if skills_meta is None:
        skills_meta = {}

    candidates = get_learning_candidates(career_reqs, user_skills, skills_meta)
    if not candidates:
        return []

    candidate_ids = {c["skill_id"] for c in candidates}
    by_id = {c["skill_id"]: c for c in candidates}

    # Build dependency graph restricted to candidates
    # in_edges[B] = set of prerequisite IDs that are also candidates and must come first
    in_edges: dict[int, set] = {sid: set() for sid in candidate_ids}
    for sid in candidate_ids:
        for prereq_id in prerequisites.get(sid, []):
            if prereq_id in candidate_ids:
                in_edges[sid].add(prereq_id)

    # Kahn's topological sort — ties broken by priority_score (descending)
    def _sort_key(sid: int) -> float:
        return by_id[sid]["priority_score"]

    ordered: list[dict] = []
    ready = sorted(
        [sid for sid, deps in in_edges.items() if not deps],
        key=_sort_key,
        reverse=True,
    )

    while ready:
        current = ready.pop(0)
        ordered.append(by_id[current])
        for sid in candidate_ids:
            if current in in_edges.get(sid, set()):
                in_edges[sid].discard(current)
                if not in_edges[sid]:
                    ready.append(sid)
                    ready.sort(key=_sort_key, reverse=True)

    # Append any remaining nodes (only reachable if the data contains a cycle)
    remaining_ids = candidate_ids - {s["skill_id"] for s in ordered}
    ordered.extend(by_id[sid] for sid in sorted(remaining_ids))

    return ordered


# ===========================================================================
# 7. Internal helper (used by api.py for the per-skill analysis table)
# ===========================================================================

def compute_skill_analysis(
    career_reqs: dict,
    user_skills: dict,
    prerequisites: dict,
    skills_meta: Optional[dict] = None,
) -> list[dict]:
    """
    Return a per-skill analysis table covering ALL skills required by the career
    (not just candidates), sorted by priority_score descending.

    Each row contains:
      skill_id, skill_name, category,
      current_level, required_level,
      gap, gap_score, skill_match,
      importance, market_demand, strategic_value,
      priority_score,
      is_candidate, is_blocked, blocked_by (list of skill names)

    Used by api.py to populate the Skill Gap page table.
    """
    if skills_meta is None:
        skills_meta = {}

    results = []

    for skill_id, req in career_reqs.items():
        current = user_skills.get(skill_id, 0)
        req_level = req["required_level"]
        imp = req["importance"]
        demand = req["market_demand"]
        strat = req["strategic_value"]

        gap = calculate_skill_gap(req_level, current)
        gs = calculate_gap_score(gap)
        sm = calculate_skill_match(current, req_level)
        ps = calculate_priority_score(gs, imp, demand, strat)

        is_candidate = gap > 0

        # Prerequisite blocking (only meaningful for candidates)
        blocked_by_names: list[str] = []
        if is_candidate:
            block_info = check_prerequisite_block(skill_id, prerequisites, career_reqs, user_skills)
            blocked_by_names = [
                skills_meta.get(bid, {}).get("skill_name", str(bid))
                for bid in block_info["blocked_by_ids"]
            ]

        meta = skills_meta.get(skill_id, {})
        results.append({
            "skill_id": skill_id,
            "skill_name": meta.get("skill_name", str(skill_id)),
            "category": meta.get("category", ""),
            "current_level": current,
            "required_level": req_level,
            "gap": gap,
            "gap_score": round(gs, 2),
            "skill_match": round(sm, 2),
            "importance": imp,
            "market_demand": demand,
            "strategic_value": strat,
            "priority_score": round(ps, 2),
            "is_candidate": is_candidate,
            "is_blocked": len(blocked_by_names) > 0,
            "blocked_by": blocked_by_names,
        })

    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return results


# ===========================================================================
# 8. Backward-compatible aliases (keep api.py working without changes)
# ===========================================================================

# Formula aliases
skill_gap = calculate_skill_gap
gap_score = calculate_gap_score
skill_match = calculate_skill_match
priority_score = calculate_priority_score

# Analysis aliases
compute_career_fit = calculate_career_fit
build_roadmap = generate_learning_roadmap


def get_recommendation(skill_analysis: list[dict]) -> Optional[dict]:
    """
    Backward-compatible wrapper: accepts a pre-computed skill_analysis list
    (as returned by compute_skill_analysis) and returns the top unblocked candidate.
    Used by legacy callers; prefer recommend_next_skill() for new code.
    """
    for skill in skill_analysis:
        if skill.get("is_candidate") and not skill.get("is_blocked"):
            return skill
    return None
