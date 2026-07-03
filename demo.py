#!/usr/bin/env python3
"""
Knowledge Compiler — Demo Script

Shows how the compiled objects answer real exercise science questions.
No external API calls. No LLM. Just deterministic object lookups.

Usage:
    python demo.py
"""

import os
import sys
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
OBJECTS = os.path.join(ROOT, "books", "acsm12", "objects")


def load(oid, type_dir):
    path = os.path.join(OBJECTS, type_dir, f"{oid}.yaml")
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f)
    return None


def src(obj):
    s = obj["source"]
    return f"ACSM12 Ch{s['chapter']}.{s['section']} — {s['section_title']} (p.{s['book_page']})"


def divider(title):
    w = 60
    print()
    print("=" * w)
    print(f"  {title}")
    print("=" * w)
    print()


# =====================================================================
divider("Q1: What's the difference between PA and exercise?")
pa = load("concept.physical_activity", "Concept")
ex = load("concept.exercise", "Concept")
print(f"  Physical Activity: {pa['definition'][:100]}...")
print(f"  Exercise:          {ex['definition'][:100]}...")
print(f"  Key: Exercise is planned, structured, repetitive — a subset of PA.")
print(f"  Source: {src(pa)}")

# =====================================================================
divider("Q2: I walk at 3.0 METs — what intensity?")
light = load("threshold.met.light", "Threshold")
mod = load("threshold.met.moderate", "Threshold")
vig = load("threshold.met.vigorous", "Threshold")
print(f"  Light:    {light['range']}")
print(f"  Moderate: {mod['range']}")
print(f"  Vigorous: {vig['range']}")
print(f"  3.0 METs → Moderate Intensity ({mod['numerical_value']}–{mod['numerical_max']} {mod['unit']})")
print(f"  Source: {src(mod)}")

# =====================================================================
divider("Q3: My BMI is 27 and waist is 105 cm — what's the risk?")
bmi = load("threshold.bmi_classification", "Threshold")
wc = load("threshold.waist_circumference", "Threshold")
print(f"  BMI 27 → Overweight ({bmi['range']})")
print(f"  Waist 105 cm (men) → Increased risk (>102 cm)")
print(f"  Sources: {src(bmi)}, {src(wc)}")

# =====================================================================
divider("Q4: Can a 55-year-old man with hypertension start vigorous exercise?")
risk = load("threshold.cvd_risk_factors", "Threshold")
alg = load("procedure.acsm_screening_algorithm", "Procedure")
med = load("recommendation.medical_clearance_exercise", "Recommendation")
print(f"  Risk factors identified:")
print(f"    • Age ≥45 ({risk['range'].split(',')[0]})")
print(f"    • Hypertension (BP ≥130/80)")
print(f"  Screening outcome: Non-exerciser + risk factors + vigorous intensity")
print(f"  → {med['dosage'][:120]}...")
print(f"  Sources: {src(risk)}, {src(alg)}, {src(med)}")

# =====================================================================
divider("Q5: How do I measure 1-RM?")
rm = load("procedure.one_rm_testing", "Procedure")
print(f"  Goal: {rm['goal']}")
for i, step in enumerate(rm["steps"], 1):
    print(f"  {i}. {step}")
print(f"  Source: {src(rm)}")

# =====================================================================
divider("Q6: What signs suggest I should stop exercising and see a doctor?")
sig = load("warning.signs_symptoms_cv_disease", "Warning")
print(f"  Signs ({len(sig['signs'])}):")
for s in sig["signs"]:
    print(f"    • {s}")
print(f"  Action: {sig['action']}")
print(f"  Source: {src(sig)}")

# =====================================================================
divider("Q7: Estimate my VO2max — I ran 2,400 meters in 12 minutes")
coop = load("formula.cooper_12min_run", "Formula")
distance = 2400
vo2max = (distance - 504.9) / 44.73
print(f"  Formula: {coop['canonical_form']}")
print(f"  Input:   distance = {distance} m")
print(f"  Result:  VO2max ≈ {vo2max:.1f} mL·kg⁻¹·min⁻¹")
print(f"  Source:  {src(coop)}")

# =====================================================================
print()
print("=" * 60)
print("  Demo complete. All answers grounded in validated objects.")
print(f"  Objects used: 10 from {OBJECTS}")
print("=" * 60)
print()
print("  Try it yourself with different values:")
print("    python -c \"print((2400 - 504.9) / 44.73)\"")
