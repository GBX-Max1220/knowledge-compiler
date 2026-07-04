# Mini Benchmark — Questions (ACSM Ch1-3)

> 设计 10 题，跨 Concept / Threshold / Procedure / Warning / Recommendation。
> 每类至少 2 题。用真实使用场景来提问，不要直接用 object 标题。

---

## Concept (3 题)

### Q01: PA vs Exercise
**Question:** What's the difference between physical activity and exercise?
**Expected answer:** Exercise is a subset of physical activity — it is planned, structured, and repetitive. Physical activity is any bodily movement produced by skeletal muscles that results in energy expenditure.
**Source objects:** `concept.physical_activity`, `concept.exercise`
**Source pages:** Ch1.2 (p.70-71)

### Q02: MET definition
**Question:** What does MET measure and what is 1 MET equivalent to?
**Expected answer:** MET (Metabolic Equivalent) measures the energy cost of physical activities. 1 MET is the energy expended at rest, approximately 3.5 mL·kg⁻¹·min⁻¹ of oxygen consumption.
**Source objects:** `concept.met`, `threshold.sedentary_met`
**Source pages:** Ch1.2 (p.71-72)

### Q03: Cardiorespiratory vs muscular fitness
**Question:** How do cardiorespiratory endurance and muscular fitness differ?
**Expected answer:** Cardiorespiratory endurance is the ability of the circulatory and respiratory systems to supply oxygen during sustained physical activity. Muscular fitness refers to the ability of muscles to generate force (strength) and sustain repeated contractions (endurance).
**Source objects:** `concept.cardiorespiratory_endurance`, `concept.muscular_strength`, `concept.muscular_endurance`
**Source pages:** Ch1.2 (p.71-73)

---

## Threshold (3 题)

### Q04: BMI 27
**Question:** I weigh 85kg and my height is 1.77m. My BMI is about 27 — what category does this fall into?
**Expected answer:** BMI 27 falls into the "Overweight" category (25.0–29.9). This is also classified as a CVD risk factor threshold (BMI ≥ 25.0 for men).
**Source objects:** `threshold.bmi_classification`, `threshold.cvd_risk_factors`
**Source pages:** Ch1.3 (p.78), Ch2.2.7 (p.142)

### Q05: Blood pressure 145/95
**Question:** A patient's resting blood pressure is 145/95 mmHg. How is this classified and what are the implications for exercise?
**Expected answer:** This is classified as Stage 1 Hypertension (systolic 130-139 or diastolic 80-89, or more broadly elevated BP ≥130/80). It counts as one CVD risk factor. Medical clearance may be needed before starting vigorous exercise.
**Source objects:** `threshold.blood_pressure_classification`, `threshold.cvd_risk_factors`, `recommendation.medical_clearance_exercise`
**Source pages:** Ch1.3 (p.78), Ch2.2.7 (p.142)

### Q06: Light vs moderate vs vigorous METs
**Question:** Walking at 3 METs, jogging at 6 METs, and running at 9 METs — what intensity categories do these fall into?
**Expected answer:** 3 METs is light intensity (1.6-2.9 METs for light... actually 3 METs is at the boundary). Moderate intensity is 3.0-5.9 METs. Vigorous is ≥6.0 METs. So 3 METs = moderate, 6 METs = vigorous, 9 METs = vigorous.
**Source objects:** `threshold.met.light`, `threshold.met.moderate`, `threshold.met.vigorous`
**Source pages:** Ch1.2 (p.71)

---

## Procedure (2 题)

### Q07: Exercise screening for sedentary adult
**Question:** A 55-year-old man with hypertension hasn't exercised regularly in years and wants to start jogging. What steps should he take before beginning?
**Expected answer:** He has CVD risk factors (age ≥45, hypertension). As a currently inactive person with 2+ risk factors wanting to do vigorous exercise, the ACSM screening algorithm recommends medical clearance before starting. He should also complete informed consent and preparticipation screening.
**Source objects:** `procedure.acsm_screening_algorithm`, `procedure.informed_consent`, `procedure.parq_plus_screening`, `recommendation.medical_clearance_exercise`
**Source pages:** Ch2.2.11 (p.150), Ch2.2 (p.130-140)

### Q08: Measuring 1-RM
**Question:** How do you safely measure someone's maximum strength in a gym setting?
**Expected answer:** Start with familiarization, warm up with submaximal weight, select initial weight at ~50-70% of perceived capacity, attempt lift with proper form, rest 3-5 minutes between attempts, increase weight gradually, stop at failure, record last successful weight. Complete within 4 trials to avoid fatigue.
**Source objects:** `procedure.one_rm_testing`
**Source pages:** Ch3.25 (p.237)

---

## Warning (2 题)

### Q09: When to stop exercising
**Question:** What physical symptoms during exercise should prompt someone to stop and seek medical evaluation?
**Expected answer:** Pain or discomfort in chest/neck/jaw/arms, shortness of breath at rest or mild exertion, dizziness or syncope, palpitations or tachycardia, leg pain or cramping, unusual fatigue, and swelling in extremities.
**Source objects:** `warning.signs_symptoms_cv_disease`
**Source pages:** Ch2.4 (p.133)

### Q10: Cardiac risk during exercise
**Question:** How common are serious cardiac events during physical activity?
**Expected answer:** SCD occurs every 1.5 million episodes of vigorous PA in men and every 36.5 million episodes of MVPA in women. But habitual physical activity reduces overall risk — the benefits far outweigh the risks. Risk is transiently higher during vigorous PA but lower in physically active individuals.
**Source objects:** `evidence.absolute_scd_risk_vigorous_pa`, `warning.scd_ami_vigorous_pa`, `evidence.inverse_msi_fitness`
**Source pages:** Ch1.10 (p.95), Ch1.11 (p.97)
