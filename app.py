"""
FlexBuddy - Intelligent Employee Team Formation System
Hackathon Prototype (rule-based, fully transparent, no ML training)

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import copy

from data import EMPLOYEES, PROJECT_PRESETS, CORE_SKILL_CATEGORIES, PHASE_WEIGHT_MULTIPLIER

st.set_page_config(page_title="FlexBuddy", page_icon="🧩", layout="wide")

# ===========================================================================
# MATCHING ENGINE (rule-based, transparent)
# ===========================================================================

def apply_phase_weighting(project_skills, phase):
    """Re-weights required skills based on project phase so that different
    phases surface different matches/teams from the same skill list.
    Weights are renormalized to preserve the original total (e.g. 100)."""
    multipliers = PHASE_WEIGHT_MULTIPLIER.get(phase, {})
    original_total = sum(v["weight"] for v in project_skills.values()) or 1

    boosted = {}
    for skill, req in project_skills.items():
        category = CORE_SKILL_CATEGORIES.get(skill, "core")
        mult = multipliers.get(category, 1.0)
        boosted[skill] = req["weight"] * mult

    boosted_total = sum(boosted.values()) or 1
    scale = original_total / boosted_total

    adjusted = {}
    for skill, req in project_skills.items():
        adjusted[skill] = {
            "required": req["required"],
            "critical": req["critical"],
            "weight": round(boosted[skill] * scale, 1),
            "original_weight": req["weight"],
        }
    return adjusted


def skill_match_score(employee, project_skills):
    """Returns (total_score 0-100, per-skill breakdown list, critical_fail list)."""
    total = 0.0
    breakdown = []
    critical_fail = []
    for skill, req in project_skills.items():
        emp_level = employee["skills"].get(skill, 0)
        required = req["required"]
        weight = req["weight"]
        contribution = min(emp_level / required, 1.0) * weight if required > 0 else weight
        total += contribution
        breakdown.append({
            "skill": skill,
            "employee_level": emp_level,
            "required_level": required,
            "weight": weight,
            "contribution": round(contribution, 1),
            "critical": req["critical"],
        })
        if req["critical"] and emp_level < required:
            critical_fail.append(skill)
    return round(total, 1), breakdown, critical_fail


def availability_score(employee):
    return employee["availability"]


def interest_match_score(employee, project_interests):
    if not project_interests:
        return 100.0
    matches = sum(1 for i in employee["interests"] if i in project_interests)
    return round((matches / len(project_interests)) * 100, 1)


def location_match_score(employee, project_location):
    if not project_location:
        return 100.0
    return 100.0 if employee["location"] == project_location else 40.0


def capacity_score(employee, assignment_workload):
    available_capacity = 100 - employee["workload"]
    if assignment_workload <= 0:
        return 100.0, available_capacity
    score = min((available_capacity / assignment_workload) * 100, 100.0)
    return round(score, 1), available_capacity


def determine_status(critical_fail, available_capacity, assignment_workload):
    if critical_fail:
        return "Not Eligible"
    if available_capacity < assignment_workload:
        return "Capacity Limited"
    return "Eligible"


def evaluate_employee(employee, project):
    sk_score, sk_breakdown, crit_fail = skill_match_score(employee, project["skills"])
    av_score = availability_score(employee)
    int_score = interest_match_score(employee, project["interests"])
    loc_score = location_match_score(employee, project.get("location"))
    cap_score, available_capacity = capacity_score(employee, project["workload"])

    final_score = (
        sk_score * 0.60
        + av_score * 0.15
        + int_score * 0.10
        + loc_score * 0.05
        + cap_score * 0.10
    )

    status = determine_status(crit_fail, available_capacity, project["workload"])

    return {
        "name": employee["name"],
        "employee": employee,
        "skill_match": round(sk_score, 1),
        "availability": av_score,
        "interest": int_score,
        "location": loc_score,
        "capacity": cap_score,
        "available_capacity": available_capacity,
        "final_score": round(final_score, 1),
        "status": status,
        "critical_fail": crit_fail,
        "skill_breakdown": sk_breakdown,
    }


def build_explanation(result, project):
    lines = []
    for row in result["skill_breakdown"]:
        if row["employee_level"] >= row["required_level"]:
            lines.append(f"✓ Strong {row['skill']} proficiency ({row['employee_level']}/5)")
        else:
            mark = "❌" if row["critical"] else "⚠️"
            lines.append(f"{mark} {row['skill']} below required level "
                         f"({row['employee_level']}/{row['required_level']})")
    if not result["critical_fail"]:
        lines.append("✓ Meets all critical skills")
    else:
        lines.append(f"❌ Missing critical skill(s): {', '.join(result['critical_fail'])}")
    lines.append(f"✓ {result['available_capacity']}% available capacity")
    if result["interest"] >= 50:
        lines.append("✓ Strong interest alignment")
    elif result["interest"] > 0:
        lines.append("~ Partial interest alignment")
    else:
        lines.append("✗ No interest overlap")
    if project.get("location") and result["location"] < 100:
        lines.append(f"~ Different location ({result['employee']['location']})")
    return lines


# ===========================================================================
# TEAM FORMATION (complementary, not just top-N)
# ===========================================================================

def form_team(results, project, team_size):
    """Greedy complementary team builder: maximizes marginal skill coverage
    while still favoring higher-scoring employees. Prefers Eligible / Capacity
    Limited candidates over Not Eligible."""
    candidates = [r for r in results if r["status"] != "Not Eligible"]
    fallback = [r for r in results if r["status"] == "Not Eligible"]
    pool = sorted(candidates, key=lambda r: r["final_score"], reverse=True) + \
        sorted(fallback, key=lambda r: r["final_score"], reverse=True)

    covered = {skill: 0 for skill in project["skills"]}
    team = []
    remaining = pool.copy()

    for _ in range(min(team_size, len(remaining))):
        best_candidate = None
        best_gain = -1
        for cand in remaining:
            gain = 0.0
            emp_skills = cand["employee"]["skills"]
            for skill, req in project["skills"].items():
                required = req["required"]
                emp_level = emp_skills.get(skill, 0)
                new_cov = min(emp_level, required)
                marginal = max(0, new_cov - covered[skill])
                gain += (marginal / required) * req["weight"] if required else 0
            # small tiebreaker nudging towards higher overall score
            combined = gain * 10 + cand["final_score"] * 0.05
            if combined > best_gain:
                best_gain = combined
                best_candidate = cand
        if best_candidate is None:
            break
        team.append(best_candidate)
        remaining.remove(best_candidate)
        emp_skills = best_candidate["employee"]["skills"]
        for skill, req in project["skills"].items():
            covered[skill] = max(covered[skill], min(emp_skills.get(skill, 0), req["required"]))

    return team, covered


def team_health_score(team, project, covered):
    if not team:
        return 0.0, {}

    # Skill coverage (50%)
    total_weight = sum(req["weight"] for req in project["skills"].values())
    coverage_points = sum(
        (covered[skill] / req["required"] if req["required"] else 1) * req["weight"]
        for skill, req in project["skills"].items()
    )
    skill_coverage = min((coverage_points / total_weight) * 100, 100) if total_weight else 100

    # Workload balance (25%) - lower spread in resulting workload = better
    workloads = [r["employee"]["workload"] for r in team]
    avg_wl = sum(workloads) / len(workloads)
    spread = (sum(abs(w - avg_wl) for w in workloads) / len(workloads))
    workload_balance = max(0, 100 - spread * 2)

    # Availability (15%)
    avg_availability = sum(r["employee"]["availability"] for r in team) / len(team)

    # Team compatibility / interest alignment (10%)
    avg_interest = sum(r["interest"] for r in team) / len(team)

    health = (
        skill_coverage * 0.50
        + workload_balance * 0.25
        + avg_availability * 0.15
        + avg_interest * 0.10
    )

    breakdown = {
        "Skill Coverage": round(skill_coverage, 1),
        "Workload Balance": round(workload_balance, 1),
        "Availability": round(avg_availability, 1),
        "Team Compatibility": round(avg_interest, 1),
    }
    return round(health, 1), breakdown


def detect_skill_gaps(project, covered):
    gaps = []
    for skill, req in project["skills"].items():
        required = req["required"]
        team_level = covered[skill]
        coverage_pct = round(min(team_level / required, 1.0) * 100, 1) if required else 100
        if coverage_pct < 100:
            gaps.append({
                "skill": skill,
                "required": required,
                "team_coverage": coverage_pct,
                "priority": "HIGH" if req["critical"] else "MEDIUM",
            })
    return gaps


def search_internal_talent(gap, team, all_employees):
    team_names = {r["name"] for r in team}
    candidates = [
        e for e in all_employees
        if e["name"] not in team_names and e["skills"].get(gap["skill"], 0) >= gap["required"]
    ]
    candidates.sort(key=lambda e: e["skills"].get(gap["skill"], 0), reverse=True)
    return candidates


ROLE_SUGGESTIONS = {
    "AWS": ("Cloud / DevOps Engineer", ["AWS", "Docker", "CI/CD"]),
    "Docker": ("Cloud / DevOps Engineer", ["AWS", "Docker", "CI/CD"]),
    "Kubernetes": ("Cloud / DevOps Engineer", ["AWS", "Docker", "Kubernetes"]),
    "CI/CD": ("DevOps Engineer", ["CI/CD", "Docker", "AWS"]),
    "NLP": ("NLP / ML Engineer", ["Python", "NLP", "MachineLearning"]),
    "MachineLearning": ("ML Engineer", ["Python", "MachineLearning", "SQL"]),
    "React": ("Frontend Engineer", ["React", "JavaScript", "CSS"]),
    "SQL": ("Data Engineer", ["SQL", "ETL", "Python"]),
    "Testing": ("QA Automation Engineer", ["Testing", "Selenium", "CI/CD"]),
    "Selenium": ("QA Automation Engineer", ["Testing", "Selenium", "CI/CD"]),
}


def recommended_role(skill):
    return ROLE_SUGGESTIONS.get(skill, (f"{skill} Specialist", [skill]))


# ===========================================================================
# UI HELPERS
# ===========================================================================

def status_badge(status):
    if status == "Eligible":
        return "🟢 Eligible"
    if status == "Capacity Limited":
        return "🟡 Capacity Limited"
    return "🔴 Not Eligible"


def health_badge(score):
    if score >= 80:
        return "🟢 GREEN / Healthy"
    if score >= 60:
        return "🟡 YELLOW / Warning"
    return "🔴 RED / Critical"


# ===========================================================================
# SIDEBAR - PROJECT CREATION
# ===========================================================================

st.sidebar.title("🧩 FlexBuddy")
st.sidebar.caption("Intelligent Employee Team Formation")

st.sidebar.header("1. Project Setup")

preset_name = st.sidebar.selectbox("Load example project", list(PROJECT_PRESETS.keys()))
preset = copy.deepcopy(PROJECT_PRESETS[preset_name])

project_name = st.sidebar.text_input("Project name", value=preset_name)
project_description = st.sidebar.text_area("Project description", value=preset["description"])
project_phase = st.sidebar.selectbox(
    "Project phase", ["Planning", "Development", "Testing", "Deployment"],
    index=["Planning", "Development", "Testing", "Deployment"].index(preset["phase"])
)

st.sidebar.subheader("Required Skills")
skills_df = pd.DataFrame([
    {"Skill": s, "Required Level (1-5)": v["required"], "Weight": v["weight"], "Critical": v["critical"]}
    for s, v in preset["skills"].items()
])
edited_skills = st.sidebar.data_editor(
    skills_df, num_rows="dynamic", use_container_width=True, key="skills_editor"
)

project_location = st.sidebar.selectbox(
    "Preferred location (optional)",
    ["Any"] + sorted({e["location"] for e in EMPLOYEES}),
    index=(["Any"] + sorted({e["location"] for e in EMPLOYEES})).index(preset.get("location", "Any"))
    if preset.get("location") in {e["location"] for e in EMPLOYEES} else 0,
)

team_size = st.sidebar.slider("Required team size", 1, 6, preset["team_size"])
project_workload = st.sidebar.slider("Project workload per member (%)", 10, 100, preset["workload"])

run_clicked = st.sidebar.button("🚀 RUN FLEXBUDDY", use_container_width=True, type="primary")

# Build project dict from edited inputs
project_skills = {}
for _, row in edited_skills.iterrows():
    if pd.isna(row["Skill"]) or str(row["Skill"]).strip() == "":
        continue
    project_skills[str(row["Skill"]).strip()] = {
        "required": int(row["Required Level (1-5)"]),
        "weight": float(row["Weight"]),
        "critical": bool(row["Critical"]),
    }

phase_adjusted_skills = apply_phase_weighting(project_skills, project_phase)

project = {
    "name": project_name,
    "description": project_description,
    "phase": project_phase,
    "skills": phase_adjusted_skills,
    "interests": preset.get("interests", []),
    "location": None if project_location == "Any" else project_location,
    "team_size": team_size,
    "workload": project_workload,
}

# ===========================================================================
# MAIN DASHBOARD
# ===========================================================================

st.title("🧩 FlexBuddy — Employee Team Formation Dashboard")

with st.expander("📄 Project Summary", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Project", project["name"])
    c2.metric("Phase", project["phase"])
    c3.metric("Team Size Needed", project["team_size"])
    st.write(project["description"])
    st.write("**Required skills (phase-adjusted weight):**", ", ".join(
        f"{s} ({v['required']}/5, w={v['weight']:.0f}{' • critical' if v['critical'] else ''})"
        for s, v in project["skills"].items()
    ))
    phase_rows = [
        {"Skill": s, "Base Weight": v["original_weight"], "Weight in " + project["phase"]: v["weight"]}
        for s, v in project["skills"].items()
    ]
    with st.expander(f"📊 Why weights shift in the **{project['phase']}** phase"):
        st.dataframe(pd.DataFrame(phase_rows), use_container_width=True, hide_index=True)
        st.caption(
            "FlexBuddy amplifies weight for skill categories that matter most in each "
            "phase (e.g. Testing boosts QA skills, Deployment boosts infra skills, "
            "Development boosts core coding skills), then renormalizes so the total "
            "stays comparable. This is why the same project can rank employees and "
            "form teams differently across phases."
        )

if not run_clicked:
    st.info("Configure the project in the sidebar, then click **🚀 RUN FLEXBUDDY** to start the demo flow.")
    st.stop()

if not project["skills"]:
    st.error("Please define at least one required skill in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# STEP 1: MATCH EMPLOYEES
# ---------------------------------------------------------------------------
st.header("2️⃣ Employee Matching & Ranking")

results = [evaluate_employee(e, project) for e in EMPLOYEES]
results.sort(key=lambda r: r["final_score"], reverse=True)

table_rows = []
for i, r in enumerate(results, start=1):
    table_rows.append({
        "Rank": i,
        "Employee": r["name"],
        "Role": r["employee"]["role"],
        "Skill Match": f"{r['skill_match']:.0f}%",
        "Availability": f"{r['availability']:.0f}%",
        "Interest": f"{r['interest']:.0f}%",
        "Capacity": f"{r['capacity']:.0f}%",
        "Final Score": f"{r['final_score']:.0f}%",
        "Status": status_badge(r["status"]),
    })
st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

st.subheader("🔍 Explainable Match Scores")
for r in results:
    with st.expander(f"Why {r['name']} scored {r['final_score']:.0f}% — {status_badge(r['status'])}"):
        col1, col2 = st.columns([1, 1])
        with col1:
            for line in build_explanation(r, project):
                st.write(line)
        with col2:
            st.write("**Score breakdown**")
            st.progress(min(r["skill_match"] / 100, 1.0), text=f"Skill Match: {r['skill_match']:.0f}%")
            st.progress(min(r["availability"] / 100, 1.0), text=f"Availability: {r['availability']:.0f}%")
            st.progress(min(r["interest"] / 100, 1.0), text=f"Interest: {r['interest']:.0f}%")
            st.progress(min(r["location"] / 100, 1.0), text=f"Location: {r['location']:.0f}%")
            st.progress(min(r["capacity"] / 100, 1.0), text=f"Capacity: {r['capacity']:.0f}%")

# ---------------------------------------------------------------------------
# STEP 2: TEAM FORMATION
# ---------------------------------------------------------------------------
st.header("3️⃣ Team Formation (Complementary, Not Just Top Scorers)")

team, covered = form_team(results, project, project["team_size"])

team_cols = st.columns(len(team)) if team else []
for col, r in zip(team_cols, team):
    with col:
        st.metric(r["name"], f"{r['final_score']:.0f}%", r["status"])
        covered_here = [s for s, req in project["skills"].items()
                         if min(r["employee"]["skills"].get(s, 0), req["required"]) > 0]
        st.caption(f"{r['employee']['role']} • {r['employee']['location']}")
        st.caption("Covers: " + ", ".join(covered_here) if covered_here else "Covers: —")

st.caption("Team built to maximize skill coverage across required skills while avoiding "
           "unnecessary duplication — not simply the highest individual scorers.")

# ---------------------------------------------------------------------------
# STEP 3: TEAM HEALTH
# ---------------------------------------------------------------------------
st.header("4️⃣ Team Health Score")

health, health_breakdown = team_health_score(team, project, covered)
hc1, hc2 = st.columns([1, 2])
with hc1:
    st.metric("TEAM HEALTH", f"{health:.0f}%", health_badge(health))
with hc2:
    for label, val in health_breakdown.items():
        st.progress(min(val / 100, 1.0), text=f"{label}: {val:.0f}%")

# ---------------------------------------------------------------------------
# STEP 4: SKILL GAP DETECTION
# ---------------------------------------------------------------------------
st.header("5️⃣ Skill Gap Detection")

gaps = detect_skill_gaps(project, covered)

gap_table = []
for skill, req in project["skills"].items():
    coverage_pct = round(min(covered[skill] / req["required"], 1.0) * 100, 1) if req["required"] else 100
    gap_table.append({
        "Skill": skill,
        "Required Level": req["required"],
        "Team Coverage": f"{coverage_pct:.0f}%",
        "Status": "✅" if coverage_pct >= 100 else "❌",
    })
st.dataframe(pd.DataFrame(gap_table), use_container_width=True, hide_index=True)

if gaps:
    for gap in gaps:
        st.warning(
            f"🚨 SKILL GAP DETECTED — **{gap['skill']}**  \n"
            f"Required Level: {gap['required']}/5  \n"
            f"Team Coverage: {gap['team_coverage']:.0f}%  \n"
            f"Priority: **{gap['priority']}**"
        )
else:
    st.success("✅ No skill gaps detected — the team fully covers all required skills.")

# ---------------------------------------------------------------------------
# STEP 5: INTERNAL TALENT SEARCH
# ---------------------------------------------------------------------------
st.header("6️⃣ Internal Talent Search")

unresolved_gaps = []
if gaps:
    for gap in gaps:
        found = search_internal_talent(gap, team, EMPLOYEES)
        if found:
            best = found[0]
            st.success(
                f"🟢 INTERNAL TALENT FOUND for **{gap['skill']}**  \n"
                f"Employee: **{best['name']}** — {gap['skill']}: {best['skills'][gap['skill']]}/5  \n"
                f"Recommendation: Add {best['name']} to the project."
            )
        else:
            st.error(f"🔴 INTERNAL TALENT NOT FOUND for **{gap['skill']}**")
            unresolved_gaps.append(gap)
else:
    st.info("No gaps to search for — team is fully covered.")

# ---------------------------------------------------------------------------
# STEP 6: RECRUITMENT ALERT
# ---------------------------------------------------------------------------
st.header("7️⃣ Recruitment Alert")

critical_unresolved = [g for g in unresolved_gaps if g["priority"] == "HIGH"]

if critical_unresolved:
    for gap in critical_unresolved:
        role, req_skills = recommended_role(gap["skill"])
        st.error(
            f"🚨 **RECRUITMENT REQUIRED**\n\n"
            f"**Missing Skill:** {gap['skill']}\n\n"
            f"**Required Level:** {gap['required']}/5\n\n"
            f"**Internal Talent:** Not Found\n\n"
            f"**Recommended Role:** {role}\n\n"
            f"**Required Skills:** {', '.join(req_skills)}"
        )
else:
    st.success("✅ No recruitment needed — all critical skill gaps are covered internally or fully met.")

st.divider()
st.caption("FlexBuddy — rule-based prototype. No ML training, no external APIs, mock data only.")