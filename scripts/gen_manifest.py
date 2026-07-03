"""Generate ACSM 12th Ed processing manifest."""
import PyPDF2, re, json

PDF = r'C:\Users\gbx12\Desktop\ACSMs Guidelines for Exercise Testing and Prescription 12th Edition.pdf'
f = open(PDF, 'rb')
reader = PyPDF2.PdfReader(f)
total_pages = len(reader.pages)

# Chapter-level data from PDF outline
CH_STRUCTURE = [
    (1, "Benefits and Risks Associated With Physical Activity", 69, 121, [
        "Introduction", "Physical Activity and Fitness Terminology",
        "Public Health Perspective for Current Recommendations",
        "Sedentary Behavior and Health",
        "Health Benefits of Regular Physical Activity and Exercise",
        "Health Benefits of Improving Muscular Fitness",
        "Risks Associated With Physical Activity and Exercise",
        "Exercise-Related Musculoskeletal Injury",
        "Sudden Cardiac Death Among Young Individuals",
        "Exercise-Related Cardiac Events in Adults",
        "Exercise Testing and the Risk of Cardiac Events",
        "Risks of Cardiac Events During Cardiac Rehabilitation",
        "Prevention of Exercise-Related Cardiac Events",
        "Online Resources", "References"
    ]),
    (2, "Preparticipation Evaluation", 122, 167, [
        "Introduction", "Informed Consent",
        "Exercise Preparticipation Health Screening",
        "American College of Sports Medicine Preparticipation Screening Process",
        "American College of Sports Medicine Preparticipation Screening Algorithm",
        "Algorithm Components", "Using the Algorithm",
        "Alternative Self-Guided Method", "Exercise Testing",
        "Risk Stratification for Individuals With Clinical Conditions and Medical Fitness Facilities",
        "Medical History and Cardiovascular Disease Risk Factor Assessment",
        "Additional Recommendations", "Online Resources", "References"
    ]),
    (3, "Health-Related Physical Fitness Testing and Interpretation", 168, 271, [
        "Introduction", "Purposes of Health-Related Physical Fitness Testing",
        "Basic Principles and Guidelines", "Pretest Instructions for Fitness Testing",
        "Organizing the Fitness Test", "Test Environment",
        "A Comprehensive Health Fitness Evaluation",
        "Measurement of Resting Heart Rate and Blood Pressure",
        "Body Composition", "Anthropometric Methods", "Densitometry",
        "Other Techniques", "Body Composition Norms",
        "Cardiorespiratory Fitness", "The Concept of Maximal Oxygen Uptake",
        "Maximal Versus Submaximal Exercise Testing",
        "Cardiorespiratory Fitness Test Sequence and Measures",
        "Test Termination Criteria", "Modes of Testing",
        "Submaximal Exercise Tests", "Interpretation of Results",
        "Muscular Fitness", "Rationale", "Principles",
        "Muscular Strength", "Muscular Endurance", "Muscular Power",
        "Flexibility", "Balance", "Online Resources", "References"
    ]),
    (4, "Clinical Exercise Testing and Interpretation", 272, 331, [
        "Introduction", "Indications for a Clinical Exercise Test",
        "Conducting the Clinical Exercise Test", "Testing Staff",
        "Testing Mode and Protocol", "Monitoring and Test Termination",
        "Postexercise", "Safety", "Interpreting the Clinical Exercise Test",
        "Heart Rate Response", "Blood Pressure Response",
        "Rate-Pressure Product", "Electrocardiogram", "Dysrhythmias",
        "Symptoms", "Exercise Capacity", "Cardiopulmonary Exercise Testing",
        "Gas Exchange Data Sampling",
        "Maximal Versus Peak Cardiorespiratory Stress",
        "Diagnostic Value of Exercise Testing for the Detection of Ischemic Heart Disease",
        "Sensitivity, Specificity, and Predictive Value",
        "Clinical Exercise Test Data and Prognosis",
        "Clinical Exercise Tests With Imaging", "Field Walking Tests",
        "Online Resources", "References"
    ]),
    (5, "General Principles of Exercise Prescription", 332, 427, [
        "An Introduction to the Principles of Exercise Prescription",
        "General Considerations for Exercise Prescription",
        "Components of the Exercise Training Session",
        "Sex Difference Considerations for Exercise Prescription and Training",
        "Sex Differences in Exercise Performance",
        "Sex Differences in Response to Exercise Training",
        "Resistance Strength Training and High-Intensity Interval Training",
        "Cardiovascular and Aerobic Endurance Training",
        "Sex Differences in Body Weight Responses to Aerobic Exercise Training",
        "Other Sex-Based Special Considerations",
        "Cardiorespiratory Fitness", "Frequency of Aerobic Exercise",
        "Intensity of Aerobic Exercise", "Time (Duration) of Aerobic Exercise",
        "Type (Mode)", "Volume (Quantity) of Aerobic Exercise",
        "Progression of Aerobic Exercise", "Resistance Training",
        "Frequency of Resistance Training Exercise",
        "Intensity of Resistance Training Exercise",
        "Time (Rest Periods of Resistance Training Exercises)",
        "Types of Resistance Training Exercises",
        "Volume of Resistance Training Exercise",
        "Progression of Resistance Training Exercise",
        "Flexibility", "Types of Flexibility Exercises",
        "Volume of Flexibility Exercise (Time, Repetitions, and Frequency)",
        "Alternatives to Stretching to Increase ROM",
        "Future Directions", "References"
    ]),
    (6, "Exercise Prescription for Healthy Populations With Special Considerations", 428, 523, [
        "Children and Adolescents", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Pregnancy", "Health Screening", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Online Resources", "Low Back Pain", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Online Resources", "Older Adults", "Exercise Testing",
        "Exercise Prescription", "Special Considerations for Exercise Programming",
        "Online Resources", "Transgender and Gender Diverse Individuals",
        "Medical Interventions", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources", "References"
    ]),
    (7, "Environmental Considerations for Exercise Prescription", 524, 573, [
        "Introduction", "Exercise in High-Altitude Environments",
        "Altitude Acclimatization", "Rapid Ascent",
        "Assessing Individual Altitude Acclimatization Status",
        "Medical Considerations: Altitude Illnesses and Preexisting Conditions",
        "Prevention and Treatment of Altitude Sickness",
        "Exercise Prescription", "Special Considerations",
        "Organizational Planning", "Exercise in Cold Environments",
        "Medical Considerations: Cold Injuries",
        "Cardiac and Respiratory Considerations",
        "Clothing Considerations", "Exercise Prescription",
        "Exercise in Hot Environments", "Mitigating Risk",
        "Medical Considerations: Exertional Heat Illnesses",
        "Exercise Prescription", "Special Considerations", "References"
    ]),
    (8, "Exercise Prescription for Individuals With Cardiovascular and Pulmonary Diseases", 574, 706, [
        "Introduction", "Coronary Heart Disease", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Cardiac Rehabilitation", "Inpatient Cardiac Rehabilitation",
        "Outpatient Cardiac Rehabilitation",
        "Continuous Electrocardiographic Monitoring",
        "Individuals With History of Spontaneous Coronary Artery Dissection",
        "Exercise Testing", "Exercise Prescription", "Special Considerations",
        "Chronic Heart Failure", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Left Ventricular Assist Device",
        "Heart Transplantation", "Exercise Testing",
        "Special Considerations", "Exercise Prescription",
        "Sternotomy", "Special Considerations",
        "Pacemaker and Implantable Cardioverter Defibrillator",
        "Special Considerations", "Peripheral Arterial Disease",
        "Exercise Testing", "Exercise Prescription", "Special Considerations",
        "Postural Orthostatic Tachycardia Syndrome",
        "Preexercise Assessment", "Exercise Prescription",
        "Special Considerations", "Pediatric Cardiac Rehabilitation",
        "Individuals With a Cerebrovascular Accident (Stroke)",
        "Exercise Testing", "Exercise Prescription",
        "Exercise Training Considerations", "Other Considerations",
        "Exercise Training for Return to Work", "Pulmonary Diseases",
        "Asthma", "Chronic Obstructive Pulmonary Disease",
        "Exercise Training for Pulmonary Diseases Other Than Chronic Obstructive Pulmonary Disease",
        "Respiratory Muscle Testing and Training",
        "Online Resources", "References"
    ]),
    (9, "Exercise Prescription for Individuals With Metabolic Disease and Cardiovascular Disease Risk Factors", 707, 783, [
        "Introduction", "Diabetes Mellitus",
        "Benefits of Regular Physical Activity for Diabetes",
        "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Dyslipidemia", "Exercise Testing", "Exercise Prescription",
        "Special Consideration", "Online Resources",
        "Hypertension", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Overweight and Obesity", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Bariatric Surgery", "Online Resources",
        "Metabolic Syndrome", "Exercise Testing",
        "Exercise Prescription/Special Considerations",
        "Online Resources",
        "Metabolic Dysfunction-Associated Steatotic Liver Disease",
        "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "References"
    ]),
    (10, "Exercise Testing and Prescription for Populations With Other Chronic Diseases and Health Conditions", 784, 960, [
        "Introduction", "Arthritis", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Online Resources", "Cancer",
        "Overview of Importance of Physical Activity in Cancer Survivors",
        "Preparticipation Evaluation", "Exercise Prescription",
        "Summary", "Online Resources", "Fibromyalgia",
        "Pharmacological Treatment Options", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Myalgic Encephalomyelitis/Chronic Fatigue Syndrome",
        "Background", "Diagnosis and Comorbidities",
        "Exercise Testing", "Pacing", "Exercise Prescription",
        "Special Considerations", "Summary", "Online Resources",
        "Human Immunodeficiency Virus", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Online Resources", "Kidney Disease", "Exercise Testing",
        "Exercise Prescription", "Special Considerations",
        "Online Resources", "Multiple Sclerosis", "Exercise Testing",
        "Exercise Testing Considerations", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Osteoporosis", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Spinal Cord Injury", "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "Online Resources",
        "Multiple Chronic Diseases and Health Conditions",
        "Exercise Testing", "Exercise Prescription",
        "Special Considerations", "References"
    ]),
    (11, "Neurologic Diseases, Conditions, and Disorders", 961, 1105, [
        "Introduction", "Anxiety and Depression", "Exercise Testing",
        "Exercise Prescription", "Exercise Considerations",
        "Special Considerations", "Future Directions",
        "Online Resources", "Anxiety", "Depression",
        "Attention-Deficit/Hyperactivity Disorder", "Exercise Testing",
        "Exercise Prescription", "Future Directions",
        "Online Resources", "Autism Spectrum Disorder",
        "Exercise Testing", "Exercise Prescription",
        "Exercise Training Considerations", "Future Directions",
        "Online Resources",
        "Intellectual Disability and Down Syndrome",
        "Exercise Testing", "Exercise Prescription",
        "Special Considerations for Individuals With Intellectual Disability",
        "Special Considerations for Individuals With Down Syndrome",
        "Future Directions", "Online Resources",
        "Cerebral Palsy", "Exercise Testing", "Exercise Prescription",
        "Future Directions", "Online Resources",
        "Alzheimer's Disease", "Exercise Testing", "Exercise Prescription",
        "Future Directions", "Online Resources",
        "Parkinson's Disease", "Exercise Testing",
        "Exercise Programming", "Special Considerations",
        "Future Directions", "Online Resources", "References"
    ]),
    (12, "Behavior-Based Strategy to Promote Physical Activity and Exercise", 1106, 1246, [
        "Introduction",
        "Theoretical Foundations for Understanding Exercise Behavior",
        "Social Cognitive Theory", "Transtheoretical Model",
        "Health Belief Model", "Social Ecological Models",
        "Self-Determination Theory", "Theory of Planned Behavior",
        "Dual-Processing Theories",
        "Relevant Targets to Promote Physical Activity Behavior Change",
        "Self-Efficacy", "Outcome Expectations and Expectancies",
        "Self-Regulation", "Autonomy", "Goal Setting", "Intention",
        "Barriers and Problem Solving", "Social Support", "Affect",
        "Motivation and Reinforcement", "Relapse Prevention",
        "Population Considerations", "Age and Lifespan",
        "Medical Status and Health Conditions", "Cultural Diversity",
        "Group Exercise Behavioral Dynamics",
        "Client-Centered Conversations and Motivational Interviewing",
        "The Role of Client-Centered Counseling",
        "Motivational Interviewing", "Online Resources", "References"
    ]),
]

# Section start pages from PDF outline (chapter-relative sub-section start pages)
SEC_PAGES = {
    1: [69, 69, 75, 82, 85, 87, 88, 89, 90, 93, 96, 98, 100, 102, 102],
    2: [122, 123, 128, 131, 136, 139, 142, 145, 146, 147, 149, 160, 161, 162],
    3: [168, 168, 169, 169, 169, 170, 171, 173, 175, 176, 187, 192, 194, 197, 198, 201, 202, 206, 206, 219, 221, 228, 229, 229, 231, 237, 239, 241, 245, 248, 249],
    4: [272, 273, 277, 279, 282, 285, 294, 294, 295, 295, 297, 298, 298, 301, 302, 302, 306, 309, 310, 311, 311, 314, 316, 318, 319, 320],
    5: [333, 334, 335, 337, 337, 340, 340, 341, 342, 343, 344, 346, 347, 357, 357, 360, 362, 363, 364, 367, 371, 372, 376, 380, 384, 390, 390, 392, 394, 395],
    6: [428, 431, 433, 437, 438, 439, 440, 443, 445, 452, 453, 454, 458, 460, 461, 463, 464, 469, 477, 482, 484, 484, 487, 488, 488, 489, 490, 490],
    7: [524, 524, 527, 529, 530, 532, 534, 535, 536, 537, 538, 540, 543, 546, 547, 548, 551, 556, 560, 561, 564],
    8: [574, 574, 575, 575, 576, 581, 581, 586, 589, 589, 590, 591, 591, 592, 593, 594, 594, 595, 596, 597, 597, 598, 600, 601, 602, 604, 605, 607, 608, 610, 612, 613, 614, 615, 617, 621, 622, 623, 624, 626, 626, 627, 628, 635, 647, 660, 665, 665],
    9: [707, 707, 711, 712, 713, 719, 724, 725, 727, 727, 729, 729, 729, 732, 733, 738, 739, 740, 743, 744, 746, 748, 749, 749, 752, 753, 755, 755, 757, 758, 760, 761],
    10: [784, 785, 787, 788, 792, 794, 794, 795, 797, 803, 812, 813, 813, 818, 821, 824, 830, 831, 831, 835, 836, 838, 839, 840, 843, 843, 844, 845, 846, 850, 850, 850, 852, 855, 859, 861, 862, 868, 868, 870, 873, 874, 874, 875, 876, 876, 879, 880, 882, 886, 895, 899, 900, 900, 901, 901, 902],
    11: [961, 963, 964, 965, 967, 971, 972, 972, 972, 973, 973, 976, 976, 978, 979, 980, 981, 985, 987, 988, 989, 990, 992, 999, 1002, 1005, 1006, 1007, 1008, 1011, 1015, 1018, 1019, 1019, 1023, 1024, 1028, 1028, 1029, 1037, 1042, 1048, 1051, 1052, 1053],
    12: [1106, 1108, 1108, 1109, 1114, 1116, 1120, 1121, 1122, 1124, 1125, 1129, 1130, 1131, 1131, 1133, 1134, 1137, 1138, 1140, 1142, 1143, 1143, 1145, 1148, 1149, 1150, 1151, 1152, 1158, 1158],
}

def count_in_range(p_start, p_end):
    text = ""
    for p in range(p_start - 1, min(p_end, total_pages)):
        try:
            text += reader.pages[p].extract_text() + "\n"
        except:
            pass
    tok = len(text) // 4
    tab = len(re.findall(r'(?i)\bTable\s+\d+\.\d+', text))
    fig = len(re.findall(r'(?i)\bFigure\s+\d+\.\d+', text))
    deff = len(re.findall(r'(?i)\bdefine\b', text))
    rec = len(re.findall(r'(?i)\brecommend\b', text))
    proc = len(re.findall(r'(?i)\bprocedure\b', text))
    thr = len(re.findall(r'(?i)\bthreshold\b', text))
    return tok, tab, fig, deff, rec, proc, thr

lines = []
lines.append("book:")
lines.append('  title: "ACSMs Guidelines for Exercise Testing and Prescription"')
lines.append("  edition: 12")
lines.append(f"  total_pages: {total_pages}")
lines.append("")
lines.append("chapters:")

for ch_num, ch_title, ch_start, ch_end, sec_titles in CH_STRUCTURE:
    pages_list = SEC_PAGES[ch_num]
    lines.append(f"- id: {ch_num}")
    lines.append(f'  title: "{ch_title}"')
    lines.append("  pdf_pages:")
    lines.append(f"    start: {ch_start}")
    lines.append(f"    end: {ch_end}")
    lines.append("  sections:")

    for si, sec_title in enumerate(sec_titles):
        s = pages_list[si]
        if si + 1 < len(pages_list):
            e = pages_list[si + 1] - 1
        else:
            e = ch_end
        if e < s:
            e = s

        n_tok, n_tab, n_fig, n_def, n_rec, n_proc, n_thr = count_in_range(s, e)
        pages_count = e - s + 1
        score = 1
        if pages_count > 3: score += 1
        if n_tab > 0: score += 1
        if n_fig > 0: score += 1
        if n_rec > 2: score += 1
        if n_proc > 0: score += 1
        if n_thr > 0: score += 1
        score = min(score, 7)

        safe_title = sec_title.replace('"', "'")
        sec_id = f"{ch_num}.{si+1}"

        lines.append(f'    - id: "{sec_id}"')
        lines.append(f'      title: "{safe_title}"')
        lines.append(f"      pdf_pages:")
        lines.append(f"        start: {s}")
        lines.append(f"        end: {e}")
        lines.append(f"      estimated_complexity: {score}")
        lines.append(f"      estimated_tokens: {n_tok}")
        lines.append(f"      contains:")
        lines.append(f'        definitions: {"yes" if n_def else "no"}')
        lines.append(f'        recommendations: {"yes" if n_rec else "no"}')
        lines.append(f'        procedures: {"yes" if n_proc else "no"}')
        lines.append(f'        tables: {"yes" if n_tab else "no"}')
        lines.append(f'        figures: {"yes" if n_fig else "no"}')
        lines.append(f'        thresholds: {"yes" if n_thr else "no"}')
        lines.append(f"      status: pending")

output = "\n".join(lines)
with open("acsms12-manifest/manifest.yaml", "w", encoding="utf-8") as fw:
    fw.write(output)
f.close()

print(f"Written {len(lines)} lines ({len(output)} bytes)")
print(f"Chapters: {len(CH_STRUCTURE)}")
total_secs = sum(len(s) for _,_,_,_,s in CH_STRUCTURE)
print(f"Total sections: {total_secs}")
