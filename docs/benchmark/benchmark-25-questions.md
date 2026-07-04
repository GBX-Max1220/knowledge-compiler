# Phase 2: 25-Question Cross-Book Benchmark

> 25 questions across ACSM (Ch1-3) and NSCA (Ch1).
> Covers: Definition, Threshold, Formula, Procedure, Multi-hop, Failure Case

---

## ACSM Questions (12)

### Definition & Concept (3)

**Q01** — What is the FITT principle and what does each letter stand for?
**Type:** Concept | **Source:** ACSM Ch5 | **Objects:** (多个 procedure)

**Q02** — What is the difference between maximal and submaximal exercise testing?
**Type:** Concept | **Source:** ACSM Ch3 | **Objects:** `concept.vo2max`

**Q03** — Define muscular strength vs muscular endurance.
**Type:** Concept | **Source:** ACSM Ch3 | **Objects:** `concept.muscular_strength`, `concept.muscular_endurance`

### Threshold (3)

**Q04** — A 45-year-old man has total cholesterol of 240 mg/dL and HDL of 35 mg/dL. How many CVD risk factors does this give him?
**Type:** Threshold + Multi-hop | **Source:** ACSM Ch1-2 | **Objects:** `threshold.cholesterol_classification`, `threshold.cvd_risk_factors`

**Q05** — What MET range corresponds to moderate intensity? Give an example activity.
**Type:** Threshold | **Source:** ACSM Ch1 | **Objects:** `threshold.met.moderate`

**Q06** — My waist circumference is 108 cm. Am I at increased risk?
**Type:** Threshold | **Source:** ACSM Ch2 | **Objects:** `threshold.waist_circumference`

### Formula (2)

**Q07** — I ran 2,800 meters in 12 minutes. Estimate my VO2max.
**Type:** Formula | **Source:** ACSM Ch3 | **Objects:** `formula.cooper_12min_run`
**Expected calc:** (2800 - 504.9) / 44.73 ≈ 51.3 mL·kg⁻¹·min⁻¹

**Q08** — A male athlete has a body density of 1.075 g/mL measured by skinfolds. Estimate his body fat percentage.
**Type:** Formula | **Source:** ACSM Ch3 | **Objects:** `formula.percent_body_fat_siri`
**Expected:** (495 / 1.075) - 450 ≈ 10.5%

### Multi-hop (2)

**Q09** — A 60-year-old woman with asthma wants to start a walking program. She has not exercised in 5 years. What screening steps should she follow before starting?
**Type:** Multi-hop | **Source:** ACSM Ch2 | **Objects:** `procedure.acsm_screening_algorithm`, `recommendation.medical_clearance_exercise`, `threshold.cvd_risk_factors`
**Expected:** Age ≥55F counts as 1 risk factor. Inactive + 1 risk factor + moderate intensity = medical clearance recommended.

**Q10** — During a submaximal exercise test, a 50-year-old man reports chest discomfort at 5 METs. What should the tester do?
**Type:** Multi-hop | **Source:** ACSM Ch2-3 | **Objects:** `warning.signs_symptoms_cv_disease`, `procedure.test_termination`
**Expected:** Stop the test immediately. Chest discomfort is a sign of possible CV disease. Seek medical evaluation.

### Procedure (2)

**Q11** — List the steps for measuring resting blood pressure.
**Type:** Procedure | **Source:** ACSM Ch2 | **Objects:** `procedure.resting_blood_pressure`

**Q12** — What are the termination criteria for an exercise test?
**Type:** Procedure | **Source:** ACSM Ch3 | **Objects:** `procedure.test_termination`

---

## NSCA Questions (8)

### Definition & Concept (2)

**Q13** — What is a sarcomere and what are its key components?
**Type:** Concept | **Source:** NSCA Ch1 | **Objects:** `concept.sarcomere`, `concept.myosin`, `concept.actin`, `concept.z_line`

**Q14** — What is the sliding-filament theory of muscle contraction?
**Type:** Concept | **Source:** NSCA Ch1 | **Objects:** `concept.sliding_filament_theory`

### Multi-hop (3)

**Q15** — A muscle fiber receives an action potential from a motor neuron. Describe the sequence of events from neural signal to muscle contraction.
**Type:** Multi-hop | **Source:** NSCA Ch1 | **Objects:** `concept.neuromuscular_junction`, `concept.action_potential`, `concept.sarcoplasmic_reticulum`, `concept.crossbridge`, `concept.sliding_filament_theory`
**Expected:** Action potential → calcium release from SR → calcium binds troponin → tropomyosin shifts → crossbridge formation → power stroke → filament sliding

**Q16** — How does bone density adapt to resistance training, and why does this matter for aging populations?
**Type:** Multi-hop | **Source:** NSCA Ch1, Ch7 | **Objects:** `concept.skeletal_system` + knowledge of aging adaptations

**Q17** — A sprinter and a marathon runner both do resistance training. Will their muscular adaptations differ? Why?
**Type:** Multi-hop | **Source:** NSCA Ch1, Ch5, Ch6 | **Objects:** multiple concept objects about fiber types, anaerobic vs aerobic

### Procedure (2)

**Q18** — How is a motor unit defined, and what determines the force produced by a muscle?
**Type:** Concept + Procedure | **Source:** NSCA Ch1 | **Objects:** `concept.motor_unit`, `concept.crossbridge`

**Q19** — What are the three types of joints classified by movement, and give an example of each?
**Type:** Concept | **Source:** NSCA Ch1 | **Objects:** `concept.uniaxial_joint`, `concept.biaxial_joint`, `concept.multiaxial_joint`

### Failure Case (1)

**Q20** — How many cervical vertebrae does a giraffe have compared to a human? (This information is NOT in the textbook.)
**Type:** Failure Case | **Source:** Out of scope
**Expected:** The textbook does not cover giraffe anatomy. A good answer should state "information not available in source material."

---

## Cross-Book Questions (5) — requires both ACSM + NSCA knowledge

### Multi-hop (3)

**Q21** — Compare the cardiovascular adaptations from ACSM's aerobic training recommendations with NSCA's resistance training adaptations. How do they differ?
**Type:** Cross-book | **Source:** ACSM Ch5 + NSCA Ch6 | **Objects:** both books' concepts

**Q22** — Both ACSM and NSCA discuss exercise prescription for older adults. What are the key considerations from each?
**Type:** Cross-book | **Source:** ACSM Ch6 + NSCA Ch7 | **Objects:** both books

**Q23** — A 45-year-old recreational athlete wants to improve both cardiovascular fitness (ACSM guidelines) and muscular strength (NSCA guidelines). How would you combine both programs?
**Type:** Cross-book synthesis | **Source:** Both books

### Comparison (2)

**Q24** — Both ACSM and NSCA define physical activity/fitness terminology. Compare how each book defines "muscular strength."
**Type:** Cross-book comparison | **Source:** ACSM Ch1 + NSCA Ch1 | **Objects:** `concept.muscular_strength` (both)

**Q25** — How do the ACSM preparticipation screening guidelines compare with the risk stratification approaches used in strength and conditioning (NSCA framework)?
**Type:** Cross-book comparison | **Source:** ACSM Ch2 + NSCA Ch23
