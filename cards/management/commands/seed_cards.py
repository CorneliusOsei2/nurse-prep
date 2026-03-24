import json
from django.core.management.base import BaseCommand
from cards.models import Category, Card

CATEGORIES = [
    {'name': 'Fundamentals', 'slug': 'fundamentals', 'icon': 'ph-bold ph-first-aid'},
    {'name': 'Pharmacology', 'slug': 'pharmacology', 'icon': 'ph-bold ph-pill'},
    {'name': 'Med-Surg', 'slug': 'medsurg', 'icon': 'ph-bold ph-heartbeat'},
    {'name': 'Pediatrics', 'slug': 'pediatrics', 'icon': 'ph-bold ph-smiley'},
    {'name': 'Maternity', 'slug': 'maternity', 'icon': 'ph-bold ph-baby'},
    {'name': 'Mental Health', 'slug': 'mental-health', 'icon': 'ph-bold ph-brain'},
    {'name': 'Leadership', 'slug': 'leadership', 'icon': 'ph-bold ph-users-three'},
]

CARDS = [
    # ── Fundamentals ──
    ('fundamentals', 'What are the normal adult vital sign ranges for temperature, pulse, respiration, and blood pressure?',
     'Temp: 97.8–99.1°F (36.5–37.3°C)\nPulse: 60–100 bpm\nResp: 12–20 breaths/min\nBP: <120/80 mmHg',
     'Knowing baseline vital sign ranges is essential for identifying abnormalities. Tachycardia (>100), bradycardia (<60), tachypnea (>20), and hypotension/hypertension require further assessment.'),

    ('fundamentals', "According to Maslow's Hierarchy of Needs, what is the priority order for nursing care?",
     'Physiological needs → Safety → Love/Belonging → Esteem → Self-Actualization.\n\nPhysiological needs (airway, breathing, circulation, food, water) always come FIRST.',
     "NCLEX often tests prioritization. A patient's physiological needs (ABCs — Airway, Breathing, Circulation) must be addressed before psychosocial needs like comfort or education."),

    ('fundamentals', 'What are the "10 Rights" of medication administration?',
     '1. Right patient\n2. Right medication\n3. Right dose\n4. Right route\n5. Right time\n6. Right documentation\n7. Right reason\n8. Right response\n9. Right to refuse\n10. Right education',
     'Medication errors are a leading cause of patient harm. Always verify at least the first 5 rights before administration. Two patient identifiers (name + DOB) must be used.'),

    ('fundamentals', 'A patient is at risk for aspiration. What position should the nurse place them in?',
     "High Fowler's position (60–90°) during and 30 minutes after eating. If unconscious, lateral (side-lying) recovery position.",
     "High Fowler's uses gravity to prevent aspiration. For unconscious patients, the lateral position allows secretions to drain from the mouth rather than into the airway."),

    ('fundamentals', 'What are the 5 stages of the nursing process?',
     'ADPIE:\n1. Assessment\n2. Diagnosis\n3. Planning\n4. Implementation\n5. Evaluation',
     'Assessment always comes first — never intervene without data. NCLEX may test which step of the nursing process a described action belongs to.'),

    ('fundamentals', 'When should a nurse perform hand hygiene? Name at least 5 moments.',
     "WHO's 5 Moments:\n1. Before patient contact\n2. Before aseptic/clean procedure\n3. After body fluid exposure\n4. After patient contact\n5. After touching patient surroundings\n\nAlso: before/after gloving, before eating.",
     'Hand hygiene is the single most important intervention to prevent healthcare-associated infections (HAIs). Use alcohol-based rub (≥20 sec) or soap and water (≥20 sec, required for C. diff and visible soiling).'),

    ('fundamentals', 'A nurse is caring for a patient on Contact Precautions. What PPE is required?',
     'Gown and gloves upon entry to the room. Dedicated equipment (stethoscope, BP cuff). Private room or cohort with same organism.',
     'Contact Precautions are used for MRSA, VRE, C. diff, scabies, and wound infections. Droplet precautions add a surgical mask. Airborne precautions require an N95 respirator and negative-pressure room.'),

    ('fundamentals', 'What does the Glasgow Coma Scale (GCS) assess, and what is the score range?',
     'Assesses level of consciousness via:\n• Eye opening (1–4)\n• Verbal response (1–5)\n• Motor response (1–6)\n\nRange: 3 (deep coma) to 15 (fully alert). Score ≤8 = severe; intubation often indicated.',
     'GCS is used for initial assessment and trending neurological status. A declining GCS score indicates worsening neurological function and requires immediate intervention.'),

    ('fundamentals', "What is informed consent, and what are the nurse's responsibilities?",
     "Informed consent requires the patient to understand the procedure, risks, benefits, and alternatives. The PROVIDER obtains consent; the NURSE witnesses the signature and ensures understanding.",
     "Nurses do not explain the procedure — that is the provider's responsibility. The nurse ensures the patient is competent, not coerced, and understands what they're consenting to."),

    ('fundamentals', 'What is the Braden Scale used for?',
     'Assesses risk for pressure injury (pressure ulcer). Six subscales: sensory perception, moisture, activity, mobility, nutrition, friction/shear.\n\nScore range: 6–23. Lower score = HIGHER risk. Score ≤18 = at risk.',
     'Pressure injuries are a key nursing-sensitive indicator. Prevention includes repositioning Q2H, moisture management, adequate nutrition (protein), and pressure-relieving devices.'),

    # ── Pharmacology ──
    ('pharmacology', 'Before administering digoxin (Lanoxin), what must the nurse assess? What is the hold parameter?',
     'Assess apical pulse for 1 FULL MINUTE.\n\nHold if:\n• Adult: HR < 60 bpm\n• Child: HR < 70 bpm\n• Infant: HR < 100 bpm\n\nAlso check potassium — hypokalemia increases digoxin toxicity risk.',
     'Digoxin slows heart rate (negative chronotropic effect). Therapeutic level: 0.8–2.0 ng/mL. Signs of toxicity: visual disturbances (yellow-green halos), bradycardia, nausea, dysrhythmias. Antidote: Digibind.'),

    ('pharmacology', 'A patient is on warfarin (Coumadin). What lab value monitors its effectiveness? What is the therapeutic range?',
     'INR (International Normalized Ratio)\n\nTherapeutic INR: 2.0–3.0 (general)\nMechanical heart valve: 2.5–3.5\n\nAlso monitor PT (prothrombin time).',
     'Warfarin inhibits vitamin K-dependent clotting factors. Antidote: Vitamin K (phytonadione). Teach patients to maintain consistent vitamin K intake, avoid NSAIDs, and report signs of bleeding.'),

    ('pharmacology', 'What is the suffix for ACE inhibitors? Name key side effects and a critical teaching point.',
     "Suffix: -pril (lisinopril, enalapril, captopril)\n\nSide effects: Persistent dry cough, hyperkalemia, angioedema (rare but serious), first-dose hypotension.\n\nTeaching: Rise slowly. Do NOT use with potassium supplements or ARBs. Contraindicated in pregnancy.",
     'ACE inhibitors are first-line for heart failure and hypertension. The dry cough occurs because ACE inhibitors prevent bradykinin breakdown. If cough is intolerable, switch to an ARB (-sartan).'),

    ('pharmacology', 'Compare the onset, peak, and duration of rapid-acting insulin (lispro/aspart) vs NPH insulin.',
     "Rapid-acting (Humalog/NovoLog):\n• Onset: 15 min\n• Peak: 1–2 hr\n• Duration: 3–4 hr\n• Given with meals\n\nNPH (intermediate):\n• Onset: 2–4 hr\n• Peak: 4–10 hr\n• Duration: 10–16 hr\n• Cloudy; roll gently, don't shake.",
     'Only regular (short-acting) and rapid-acting insulin can be given IV. When mixing insulins: draw up CLEAR (regular) before CLOUDY (NPH). Monitor for hypoglycemia at peak times.'),

    ('pharmacology', 'What suffix identifies beta-blockers? What are 3 important nursing considerations?',
     'Suffix: -olol (metoprolol, atenolol, propranolol)\n\n1. Monitor HR — hold if < 60 bpm\n2. Do NOT stop abruptly (rebound hypertension/tachycardia)\n3. May mask signs of hypoglycemia in diabetics',
     'Beta-blockers decrease heart rate, contractility, and blood pressure. Contraindicated in asthma (propranolol). Cardioselective beta-blockers (metoprolol, atenolol) are safer in lung disease at low doses.'),

    ('pharmacology', 'A patient is prescribed heparin. What lab monitors its effectiveness? What is the antidote?',
     'Lab: aPTT (activated Partial Thromboplastin Time)\nTherapeutic: 1.5–2.5× the control value (approximately 60–80 seconds)\n\nAntidote: Protamine sulfate\n\nFor LMWH (enoxaparin): monitor anti-Xa levels.',
     'Heparin is given IV or SubQ, NOT IM (risk of hematoma). Do not rub injection site. Monitor for HIT (Heparin-Induced Thrombocytopenia) — check platelet count.'),

    ('pharmacology', 'What are aminoglycoside antibiotics (gentamicin, tobramycin), and what are the two critical toxicities?',
     'Aminoglycosides treat gram-negative infections.\n\nTwo major toxicities:\n1. OTOTOXICITY — hearing loss, tinnitus, vertigo\n2. NEPHROTOXICITY — rising BUN/creatinine\n\nMonitor: trough levels, BUN, creatinine, I&O.',
     'Aminoglycosides have a narrow therapeutic index. Ensure adequate hydration. Report tinnitus or decreased hearing immediately.'),

    ('pharmacology', 'A patient on an SSRI (fluoxetine/Prozac) asks when the medication will start working. What do you teach?',
     "Full therapeutic effect: 2–6 weeks.\n\nKey teaching:\n• Do NOT stop abruptly (withdrawal symptoms)\n• Avoid alcohol\n• Report suicidal thoughts (risk increases early in treatment, especially ages 18–24)\n• Avoid MAOIs — risk of serotonin syndrome",
     "Serotonin syndrome: agitation, hyperthermia, diaphoresis, tachycardia, muscle rigidity, tremor, clonus. It is life-threatening. Also avoid combining SSRIs with St. John's Wort, tramadol, or triptans."),

    ('pharmacology', 'What is the priority nursing assessment before and after giving a blood transfusion?',
     'Before: Verify with 2 nurses — patient ID, blood type, Rh, expiration date, crossmatch.\n\nDuring first 15 min: Stay with patient; vital signs Q5min × 15 min, then Q15–30min.\n\nWatch for: Fever, chills, hives, flank pain, hypotension, dyspnea.',
     "If a reaction occurs: STOP the transfusion immediately, keep the IV open with NS, notify provider, send blood bag and tubing to the lab. Administer with NS only — never with dextrose or lactated Ringer's."),

    ('pharmacology', 'What are the signs of opioid toxicity, and what is the reversal agent?',
     'Signs: Respiratory depression (RR < 12), pinpoint pupils, excessive sedation, hypotension, bradycardia.\n\nReversal: Naloxone (Narcan) 0.4–2 mg IV/IM/SubQ/intranasal. May repeat Q2–3min.\n\nMonitor for re-sedation — naloxone has a shorter half-life than most opioids.',
     'Always assess respiratory rate before giving opioids. Hold if RR < 12. Naloxone can precipitate acute withdrawal in opioid-dependent patients.'),

    # ── Med-Surg ──
    ('medsurg', 'Compare left-sided vs right-sided heart failure symptoms.',
     'LEFT-sided (backward into lungs):\n• Dyspnea, orthopnea\n• Crackles/rales\n• Pink frothy sputum\n• Tachycardia, S3 gallop\n\nRIGHT-sided (backup into systemic circulation):\n• Peripheral edema\n• JVD (jugular vein distention)\n• Hepatomegaly\n• Weight gain, Ascites',
     '"Left = Lungs" and "Right = Rest of the body." Treatment: diuretics, ACE inhibitors, low sodium diet, daily weights, fluid restriction.'),

    ('medsurg', 'A patient presents with crushing chest pain, diaphoresis, and nausea. What are the priority nursing actions for suspected MI?',
     'MONA (modified):\n• Morphine (if pain not relieved by nitro)\n• Oxygen (if SpO₂ < 94%)\n• Nitroglycerin (SL, up to 3 doses Q5min)\n• Aspirin (160–325 mg, chewed)\n\nAlso: 12-lead ECG within 10 min, IV access, troponin levels.',
     'Time is muscle. Contraindications to nitro: hypotension (SBP < 90), recent PDE-5 inhibitor use (sildenafil within 24 hrs). Position: semi-Fowler\'s.'),

    ('medsurg', 'Differentiate DKA (Diabetic Ketoacidosis) from HHS (Hyperosmolar Hyperglycemic State).',
     'DKA (Type 1):\n• BG: 250–600 mg/dL\n• Kussmaul respirations\n• Fruity breath\n• Metabolic acidosis (pH < 7.35)\n• Positive ketones\n\nHHS (Type 2):\n• BG: > 600 mg/dL (often > 1000)\n• No significant ketosis\n• Severe dehydration\n• Altered consciousness',
     'Both: aggressive IV fluid resuscitation (NS), then insulin drip. In DKA, correct potassium BEFORE insulin if K+ is low.'),

    ('medsurg', 'A COPD patient is on 2L O₂ via nasal cannula. Why should you NOT give high-flow oxygen?',
     'COPD patients may rely on hypoxic drive to breathe. Their chemoreceptors respond to LOW O₂ levels (not high CO₂ as in healthy individuals).\n\nGiving high-flow O₂ can suppress respiratory drive → CO₂ retention → respiratory failure.\n\nKeep SpO₂ at 88–92% for COPD patients.',
     'For COPD exacerbation: bronchodilators (albuterol), corticosteroids, antibiotics if indicated, pursed-lip breathing.'),

    ('medsurg', 'What is the priority assessment for a patient with a chest tube?',
     "Assess:\n• Tidaling (normal fluctuation in water seal)\n• Continuous bubbling in water seal = air leak\n• Drainage amount, color, consistency\n• Respiratory status\n• Dressing site for crepitus\n\nNEVER clamp a chest tube without a provider's order.",
     'Tidaling is expected. If the chest tube disconnects: submerge in sterile water. If it falls out: cover with petroleum gauze, taped on 3 sides.'),

    ('medsurg', 'What are the signs and symptoms of hyperkalemia, and what is the priority intervention?',
     'Signs: Tall peaked T waves on ECG, muscle weakness, paresthesias, bradycardia → cardiac arrest.\n\nNormal K+: 3.5–5.0 mEq/L\n\nPriority interventions:\n1. Calcium gluconate IV (cardiac protection)\n2. Insulin + glucose (shifts K+ into cells)\n3. Kayexalate (removes K+ via GI)\n4. Dialysis (severe cases)',
     'Hyperkalemia is a medical emergency when K+ > 6.0 or ECG changes present. Causes: renal failure, ACE inhibitors, potassium-sparing diuretics, crush injuries.'),

    ('medsurg', 'Using the Rule of Nines, estimate the TBSA burned for an adult with burns to the entire right arm and anterior trunk.',
     'Right arm (entire) = 9%\nAnterior trunk = 18%\nTotal = 27% TBSA\n\nRule of Nines (adult):\n• Head = 9%\n• Each arm = 9%\n• Anterior trunk = 18%\n• Posterior trunk = 18%\n• Each leg = 18%\n• Perineum = 1%',
     "TBSA determines fluid resuscitation needs. Parkland formula: 4 mL × kg × %TBSA = total fluids in first 24 hrs (half in first 8 hrs, half in next 16 hrs, using Lactated Ringer's)."),

    ('medsurg', "What are the 5 P's of neurovascular assessment, and when are they used?",
     '1. Pain (out of proportion)\n2. Pallor (pale, cool skin)\n3. Pulselessness (diminished/absent distal pulse)\n4. Paresthesia (numbness, tingling)\n5. Paralysis (inability to move — late sign)\n\nUsed for: fractures, casts, compartment syndrome, post-vascular surgery.',
     'Compartment syndrome is a surgical emergency. Unrelenting pain not relieved by opioids is the earliest sign. Treatment: fasciotomy.'),

    ('medsurg', 'A patient with liver cirrhosis develops hepatic encephalopathy. What are the dietary and medication interventions?',
     'Diet: Restrict PROTEIN (ammonia is a byproduct of protein metabolism)\n\nMedications:\n• Lactulose — traps ammonia in the gut; expect 2–3 soft stools/day\n• Rifaximin — reduces ammonia-producing bacteria\n\nMonitor: ammonia levels, neurological status (asterixis = liver flap).',
     'Hepatic encephalopathy occurs when the damaged liver cannot convert ammonia to urea. Monitor for dehydration with lactulose.'),

    ('medsurg', 'What are the four types of shock and their primary characteristics?',
     '1. Hypovolemic — fluid/blood loss; ↓BP, ↑HR, cool/clammy skin\n2. Cardiogenic — pump failure (MI); ↓BP, ↑HR, JVD, crackles\n3. Distributive — vasodilation (septic, anaphylactic, neurogenic)\n4. Obstructive — physical obstruction (PE, tension pneumothorax, tamponade)',
     'All shock → inadequate tissue perfusion. Septic shock: warm/flushed initially, then cool. Treatment: fluids for hypovolemic; vasopressors for distributive; treat underlying cause.'),

    # ── Pediatrics ──
    ('pediatrics', 'How do you differentiate epiglottitis from croup in a child?',
     "CROUP (laryngotracheobronchitis):\n• Viral, gradual onset\n• Barking/seal-like cough\n• Steeple sign on X-ray\n• Low-grade fever\n\nEPIGLOTTITIS:\n• Bacterial (H. influenzae), sudden onset\n• Drooling, dysphagia, distress (3 D's)\n• Tripod positioning\n• Thumb sign on X-ray\n• HIGH fever\n• DO NOT examine throat!",
     'Epiglottitis is a medical emergency. Do NOT use a tongue depressor. Keep the child calm, prepare for intubation. Croup treatment: cool mist, racemic epinephrine, corticosteroids.'),

    ('pediatrics', 'What are the signs of dehydration in an infant?',
     'Mild: slightly dry mucous membranes, decreased tears\n\nModerate: sunken fontanelle, decreased skin turgor (tenting), decreased urine output (<1 mL/kg/hr), tachycardia\n\nSevere: absent tears, very sunken fontanelle, mottled/cool skin, lethargy, capillary refill >3 sec',
     'Infants are at higher risk for dehydration due to higher body water percentage and immature kidneys. Monitor weight (best indicator), I&O, specific gravity (>1.030 = concentrated).'),

    ('pediatrics', 'An infant with pyloric stenosis presents with what classic symptom? What are the key findings?',
     'Classic: Projectile, non-bilious vomiting (2–6 weeks of age)\n\nFindings:\n• Olive-shaped mass in RUQ\n• Visible peristaltic waves (left to right)\n• Hungry after vomiting\n• Metabolic alkalosis (loss of HCl)\n\nDiagnosis: ultrasound\nTreatment: pyloromyotomy',
     'The vomiting is non-bilious because the obstruction is proximal to the bile duct. Correct dehydration and electrolytes before surgery.'),

    ('pediatrics', 'What are the key nursing interventions for a child in sickle cell crisis (vaso-occlusive)?',
     '1. PAIN management — opioids (priority!)\n2. HYDRATION — IV fluids (dilutes blood)\n3. OXYGEN — maintain SpO₂ > 95%\n4. REST — bedrest during acute phase\n5. WARMTH — avoid cold (causes vasoconstriction)\n\nAvoid: high altitudes, dehydration, infection, strenuous exercise.',
     'Monitor for acute chest syndrome (fever, chest pain, infiltrate on CXR) — leading cause of death. Hydroxyurea reduces crisis frequency.'),

    ('pediatrics', 'What are the classic signs of Kawasaki disease?',
     "CRASH and BURN mnemonic:\n• Conjunctivitis (bilateral, non-purulent)\n• Rash (polymorphous)\n• Adenopathy (cervical, usually unilateral)\n• Strawberry tongue (+ cracked red lips)\n• Hands & feet (edema, peeling)\n• BURN = fever ≥ 5 days (required criterion)\n\nComplication: Coronary artery aneurysms",
     'Treatment: HIGH-dose IVIG + aspirin (one of the few times aspirin is used in children). Echocardiograms to monitor for coronary artery changes.'),

    ('pediatrics', 'At what developmental milestones can an infant/toddler: sit unsupported, walk, and speak 2-word phrases?',
     '• Sits unsupported: ~6 months\n• Pulls to stand: ~9 months\n• Walks independently: ~12 months\n• 2-word phrases ("mama up"): ~18–24 months\n\nRule of thumb: If not walking by 18 months or no words by 16 months — developmental screening needed.',
     'Other milestones: social smile (2 mo), rolls over (4–5 mo), pincer grasp (9–10 mo), says 2–3 words (12 mo), stacks 2 blocks (15 mo).'),

    ('pediatrics', 'How do pediatric medication doses differ, and what is the most common method of calculation?',
     'Pediatric doses are calculated based on WEIGHT (mg/kg).\n\nSteps:\n1. Verify weight in kg (1 kg = 2.2 lbs)\n2. Calculate safe dose range (mg/kg/dose or mg/kg/day)\n3. Compare ordered dose to safe range\n4. If outside range — hold & notify provider\n\nAlways double-check pediatric calculations.',
     'Children are NOT small adults — they metabolize drugs differently. BSA (body surface area) is also used for chemotherapy dosing.'),

    ('pediatrics', 'What positioning is used after a cleft lip repair vs cleft palate repair?',
     'Cleft LIP repair: Position on BACK or side (NOT prone) to protect the suture line. Use Logan bow/steri-strips.\n\nCleft PALATE repair: Position PRONE or side-lying to promote drainage and prevent aspiration.\n\nBoth: Use elbow restraints, avoid straws/spoons/pacifiers.',
     'Key difference: Lip repair = protect suture line, so keep face up. Palate repair = prevent aspiration, so keep face down.'),

    # ── Maternity ──
    ('maternity', 'What is the APGAR scoring system, and when is it assessed?',
     'Assessed at 1 minute and 5 minutes after birth.\n\nA — Appearance (skin color)\nP — Pulse (heart rate)\nG — Grimace (reflex irritability)\nA — Activity (muscle tone)\nR — Respiration\n\nEach scored 0–2. Total: 0–10.\n• 7–10: Normal\n• 4–6: Needs intervention\n• 0–3: Emergency resuscitation',
     '1-minute APGAR indicates need for immediate intervention. 5-minute APGAR reflects response to resuscitation. Heart rate is the most critical indicator.'),

    ('maternity', 'What are the warning signs of preeclampsia, and when does it become severe?',
     'Preeclampsia (≥20 weeks gestation):\n• BP ≥ 140/90 on 2 occasions\n• Proteinuria\n• Edema (face/hands)\n\nSEVERE preeclampsia:\n• BP ≥ 160/110\n• Severe headache\n• Visual changes\n• Epigastric/RUQ pain\n• Elevated liver enzymes, low platelets (HELLP)\n• Hyperreflexia/clonus',
     'Treatment: Magnesium sulfate (seizure prevention — therapeutic level 4–7 mEq/L). Antidote: Calcium gluconate. Monitor: DTRs, RR (<12), UO (<30 mL/hr). Definitive treatment: DELIVERY.'),

    ('maternity', 'What are the four stages of labor?',
     'Stage 1: Cervical dilation & effacement (0–10 cm)\n  • Latent phase: 0–6 cm (longest)\n  • Active phase: 6–10 cm\n\nStage 2: Full dilation to delivery of baby\n\nStage 3: Delivery of placenta (5–30 min)\n\nStage 4: Recovery — first 1–2 hours postpartum (monitor for hemorrhage)',
     'Stage 1 is the longest. Stage 4: assess fundus (should be firm at or below umbilicus), lochia, vitals Q15min.'),

    ('maternity', 'What fetal heart rate (FHR) patterns are reassuring vs non-reassuring?',
     'REASSURING:\n• Baseline: 110–160 bpm\n• Moderate variability (6–25 bpm)\n• Accelerations present\n• Early decelerations (head compression)\n\nNON-REASSURING:\n• Late decelerations (uteroplacental insufficiency)\n• Variable decelerations with slow recovery\n• Absent variability\n• Bradycardia (<110) or tachycardia (>160)',
     'Late decels: reposition mom (left lateral), stop Pitocin, give O₂, increase IV fluids, notify provider.'),

    ('maternity', 'What is Rh incompatibility, and how is it managed?',
     "Occurs when Rh-negative mother carries Rh-positive fetus. Mother's immune system may create antibodies against fetal Rh+ blood cells.\n\nPrevention: RhoGAM (Rh immune globulin)\n• Given at 28 weeks gestation\n• Given within 72 hours postpartum (if newborn is Rh+)\n• Given after any bleeding, amniocentesis, miscarriage, or ectopic pregnancy.",
     'RhoGAM prevents maternal antibody formation (isoimmunization). Indirect Coombs test checks mother for antibodies. Direct Coombs checks the newborn.'),

    ('maternity', 'What are the signs of postpartum hemorrhage, and what are the nursing priorities?',
     "PPH: blood loss > 500 mL (vaginal) or > 1000 mL (C-section)\n\nSigns: boggy uterus, heavy bleeding, tachycardia, hypotension\n\nNursing priorities (4 T's of causes):\n1. Tone — fundal massage (#1 intervention)\n2. Tissue — retained placenta\n3. Trauma — lacerations\n4. Thrombin — coagulopathy\n\nMedications: oxytocin, methylergonovine, carboprost",
     'PPH is a leading cause of maternal death. A full bladder can displace the uterus and impede contraction — catheterize if needed.'),

    ('maternity', 'What should the nurse teach about breastfeeding positioning and latch?',
     'Proper latch:\n• Baby\'s mouth covers nipple + areola\n• Lips flanged outward ("fish lips")\n• Audible swallowing\n• No pain after initial latch\n\nPositions: cradle, cross-cradle, football (C-section), side-lying\n\nFeed Q2–3 hrs (8–12×/day). Both breasts per feeding.',
     'Breast milk supply works on supply-and-demand. Encourage skin-to-skin within 1 hour of birth. Signs of adequate intake: 6+ wet diapers/day, 3+ stools/day, steady weight gain.'),

    ('maternity', 'What is gestational diabetes, and how is it managed?',
     'Glucose intolerance first identified in pregnancy (usually 24–28 weeks).\n\nScreening: 1-hour glucose challenge (≥140 → 3-hour GTT)\n\nManagement:\n• Diet: controlled carbs, small frequent meals\n• Exercise: 30 min/day\n• BG monitoring: fasting < 95, 2-hr postprandial < 120\n• Insulin if diet/exercise fail\n\nRisks: macrosomia, neonatal hypoglycemia',
     'Gestational diabetes increases risk for Type 2 DM later. Newborns need early feeding and glucose monitoring.'),

    # ── Mental Health ──
    ('mental-health', 'What are therapeutic communication techniques? Name at least 5.',
     '1. Active listening (most important)\n2. Open-ended questions ("Tell me more about…")\n3. Reflecting/restating ("So you\'re feeling…")\n4. Silence (allows processing)\n5. Clarifying ("What do you mean by…")\n6. Summarizing\n7. Focusing\n8. Offering self ("I\'ll sit with you")\n\nNON-therapeutic: giving advice, false reassurance, "why" questions, changing the subject.',
     '"How does that make you feel?" is almost always correct. Avoid "Don\'t worry" (false reassurance), "Why did you…" (defensive), "I know exactly how you feel" (belittling).'),

    ('mental-health', "A patient expresses suicidal ideation. What is the nurse's priority action?",
     'Priority: Assess for a PLAN — "Are you thinking of hurting yourself? Do you have a plan? Do you have the means?"\n\nActions:\n1. Stay with the patient (1:1 observation)\n2. Remove harmful objects\n3. Establish a safe environment\n4. Notify provider immediately\n5. Document assessment\n\nDo NOT leave the patient alone. Do NOT promise confidentiality.',
     'Risk factors: previous attempt (strongest predictor), access to means, substance abuse, hopelessness, social isolation, recent loss.'),

    ('mental-health', 'What are the signs and stages of alcohol withdrawal, and what is the CIWA scale?',
     'Timeline after last drink:\n• 6–12 hrs: tremors, anxiety, tachycardia, diaphoresis\n• 12–24 hrs: hallucinations (visual)\n• 24–48 hrs: seizures (grand mal)\n• 48–96 hrs: Delirium tremens (DTs) — confusion, severe agitation, LIFE-THREATENING\n\nCIWA-Ar: scores 0–67; ≥ 8 = medicate with benzodiazepines.',
     'Alcohol withdrawal can be fatal. Treatment: benzodiazepines (lorazepam, chlordiazepoxide). Also: thiamine (B1) BEFORE glucose (prevents Wernicke encephalopathy).'),

    ('mental-health', 'A patient with bipolar disorder is prescribed lithium. What are the key monitoring parameters?',
     'Therapeutic level: 0.6–1.2 mEq/L\nToxic: > 1.5 mEq/L\nLethal: > 2.0 mEq/L\n\nMonitoring:\n• Lithium level (drawn 12 hrs after last dose)\n• Renal function (BUN, creatinine)\n• Thyroid function (can cause hypothyroidism)\n• Sodium level (low Na+ → lithium toxicity)\n\nToxicity signs: GI distress → coarse tremors → confusion → seizures → death',
     'Lithium has a very narrow therapeutic index. Teach: maintain adequate sodium and fluid intake, avoid NSAIDs and ACE inhibitors (increase lithium levels).'),

    ('mental-health', 'What are the key nursing interventions for a patient experiencing a panic attack?',
     '1. Stay with the patient — calm, reassuring presence\n2. Move to a quiet environment\n3. Use simple, direct instructions\n4. Encourage slow, deep breathing (diaphragmatic)\n5. Speak in short, clear sentences\n6. Do NOT ask the patient to explain during the attack\n\nMedication: Short-acting benzodiazepine (lorazepam) for acute episodes.',
     'During a panic attack, the person cannot process complex information. Once it subsides, teach coping strategies: grounding techniques (5-4-3-2-1), progressive muscle relaxation.'),

    ('mental-health', 'What are the positive and negative symptoms of schizophrenia?',
     'POSITIVE (excess/distortion):\n• Hallucinations (auditory most common)\n• Delusions (fixed false beliefs)\n• Disorganized speech/behavior\n• Paranoia\n\nNEGATIVE (deficit):\n• Flat affect\n• Alogia (poverty of speech)\n• Avolition (lack of motivation)\n• Anhedonia (no pleasure)\n• Social withdrawal\n\nTypical antipsychotics treat positive. Atypical (clozapine, risperidone) treat both.',
     'Clozapine: most effective for treatment-resistant schizophrenia but requires weekly WBC/ANC monitoring (risk of agranulocytosis). Monitor for EPS and metabolic syndrome.'),

    ('mental-health', "What are the nurse's legal and ethical considerations for restraint use?",
     'Restraints are LAST RESORT.\n\nRequirements:\n• Physician order (time-limited: 4 hrs adult, 2 hrs 9–17 y/o, 1 hr <9 y/o)\n• Face-to-face evaluation within 1 hour\n• Assessment Q15min–1hr (circulation, sensation, movement)\n• Release Q2hrs for ROM, toileting, nutrition\n• Document behavior requiring restraints\n• Least restrictive method first\n\nNever tie to side rails. Always ensure quick-release knots.',
     'Alternatives to try first: therapeutic communication, de-escalation, redirection, environmental modification, 1:1 sitter.'),

    ('mental-health', 'Differentiate anorexia nervosa from bulimia nervosa.',
     "ANOREXIA NERVOSA:\n• Severe weight restriction (BMI < 17.5)\n• Fear of gaining weight\n• Distorted body image\n• Amenorrhea\n• Lanugo, bradycardia, hypothermia\n\nBULIMIA NERVOSA:\n• Binge-purge cycles\n• Usually normal weight\n• Russell's sign (knuckle calluses)\n• Dental erosion, parotid gland swelling\n• Metabolic alkalosis (from vomiting)\n• Hypokalemia",
     'Anorexia: highest mortality of any psychiatric disorder. Refeeding syndrome is a serious risk — monitor phosphorus, potassium, magnesium.'),

    # ── Leadership ──
    ('leadership', 'What tasks can a nurse delegate to a UAP (Unlicensed Assistive Personnel)?',
     'UAPs CAN do:\n• Vital signs (stable patients)\n• I&O measurement\n• Daily weights\n• Bathing, feeding, ambulation\n• Specimen collection\n• Blood glucose monitoring (fingerstick)\n\nUAPs CANNOT do:\n• Assessment or evaluation\n• Teaching\n• Medication administration\n• Nursing judgment decisions\n• IV management',
     'Use the 5 Rights of Delegation: Right task, Right circumstance, Right person, Right communication, Right supervision. The RN ALWAYS retains accountability.'),

    ('leadership', 'An RN is caring for 4 patients. Which should be seen FIRST?\nA) Post-op day 1, pain 6/10\nB) New admission with chest pain\nC) Diabetic patient, BG 180\nD) Patient requesting discharge papers',
     'B) New admission with chest pain.\n\nPriority framework (ABC + acute before chronic):\n1. Airway, Breathing, Circulation threats\n2. Acute/unstable conditions\n3. Newly assessed/changed status\n4. Chronic/stable conditions\n5. Health maintenance/education\n\nChest pain = potential cardiac emergency.',
     'The post-op pain is expected, the BG 180 is slightly elevated but not critical, and discharge papers are administrative. Always address life-threatening changes first.'),

    ('leadership', 'What is the difference between RN and LPN/LVN scope of practice?',
     'RN can:\n• Perform initial assessment & develop care plan\n• Administer IV push medications\n• Administer blood products\n• Teach patients\n• Delegate to LPN/UAP\n• Manage unstable patients\n\nLPN/LVN can:\n• Perform focused assessment (data collection)\n• Administer oral/IM/SubQ/some IV meds\n• Reinforce (not initiate) teaching\n• Care for STABLE patients',
     'Assign stable, predictable patients to LPNs. Assign new admissions, post-op patients, unstable conditions, blood transfusions, and IV push meds to the RN.'),

    ('leadership', "A nurse witnesses a medication error. What is the correct sequence of actions?",
     "1. Assess the patient (priority — check for adverse effects)\n2. Notify the provider\n3. Implement corrective actions as ordered\n4. Document the event in the patient's chart (objective facts only)\n5. Complete an incident/occurrence report (NOT placed in the chart)\n6. Notify the charge nurse/supervisor\n\nDo NOT document 'incident report filed' in the chart.",
     'Incident reports are for quality improvement, not punitive action. They are confidential documents. Document factually, without blame or opinions.'),

    ('leadership', 'What is SBAR communication, and when is it used?',
     'S — Situation: "I\'m calling about Mr. Jones in room 302. He\'s having difficulty breathing."\n\nB — Background: "He\'s a 68-year-old admitted for CHF, on 2L O₂."\n\nA — Assessment: "His SpO₂ dropped to 88%, crackles in bilateral bases, RR 28."\n\nR — Recommendation: "I think he needs a diuretic and chest X-ray."',
     "SBAR standardizes communication between healthcare providers to reduce errors. It's used during handoff, when calling a provider, and during rapid response situations."),

    ('leadership', 'In a mass casualty/triage situation, what do the triage colors mean?',
     'RED (Immediate): Life-threatening but salvageable.\nYELLOW (Delayed): Serious but can wait hours.\nGREEN (Minor/Walking Wounded): Minor injuries, can wait.\nBLACK (Expectant): Dead or will not survive even with treatment.',
     'In mass casualty triage, the goal shifts from saving every life to saving the MOST lives. A patient who would normally receive aggressive treatment may be tagged black in a disaster.'),
]


class Command(BaseCommand):
    help = 'Seed the database with default NCLEX flashcard categories and cards'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete all existing default cards before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            Card.objects.filter(is_default=True).delete()
            Category.objects.filter(is_default=True).delete()
            self.stdout.write('Cleared existing default data.')

        # Create categories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'icon': cat_data['icon'], 'is_default': True}
            )
            cat_map[cat_data['slug']] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {cat}')

        # Create cards
        created_count = 0
        for slug, question, answer, rationale in CARDS:
            _, created = Card.objects.get_or_create(
                question=question,
                defaults={
                    'category': cat_map[slug],
                    'answer': answer,
                    'rationale': rationale,
                    'is_default': True,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created_count} cards across {len(CATEGORIES)} categories.'))
