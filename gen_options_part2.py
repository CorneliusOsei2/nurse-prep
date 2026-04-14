#!/usr/bin/env python3
"""Generate MCQ options for Exam #1 section flashcards."""

import re

FILEPATH = '/Users/cornelius/Desktop/code/flashcards/data/pharmacology/exam-1/exam-1-flashcards.md'

# (front_text, [option_A, option_B, option_C, option_D], correct_letter)
CARD_DATA = {
    12: (
        'A nurse gave the wrong dose of a medication. The patient seems fine right now. What should the nurse do FIRST?',
        [
            'Assess the patient for any adverse effects',
            'File an incident report with the charge nurse',
            'Call the pharmacy to verify the correct dose',
            'Administer an antidote as a precaution',
        ],
        'A',
    ),
    13: (
        'Which statement correctly matches each analgesic class with its primary safety concern?',
        [
            'Acetaminophen causes GI bleeding; NSAIDs cause liver damage; Opioids cause kidney failure',
            'Acetaminophen causes liver damage; NSAIDs cause GI bleeding and kidney problems; Opioids cause respiratory depression',
            'Acetaminophen causes respiratory depression; NSAIDs cause liver toxicity; Opioids cause GI bleeding',
            'Acetaminophen causes kidney damage; NSAIDs cause sedation; Opioids cause liver damage',
        ],
        'B',
    ),
    14: (
        'What is the most important warning about naloxone (Narcan) when used to reverse opioid toxicity?',
        [
            'Naloxone can cause permanent liver damage if given more than once',
            'Naloxone should only be administered by the IV route to be effective',
            'Naloxone wears off faster than most opioids, so respiratory depression may return',
            'Naloxone eliminates all opioid effects permanently after a single dose',
        ],
        'C',
    ),
    15: (
        'A patient received IV morphine 30 minutes ago. You check on them and their respiratory rate is 10. What is your priority?',
        [
            'Document the respiratory rate and recheck in one hour',
            'Administer the next scheduled dose of morphine on time',
            'Stay with the patient, stimulate them, and prepare naloxone if breathing does not improve',
            'Call the pharmacy to change the morphine to an oral form',
        ],
        'C',
    ),
    16: (
        'After giving IV morphine, which of the following findings needs immediate action?',
        [
            'The patient says "I feel a little itchy"',
            'Respiratory rate drops to 8',
            'The patient reports mild nausea',
            'The patient reports mild constipation',
        ],
        'B',
    ),
    17: (
        'Which of the following best describes what a nurse should reassess after giving an opioid pain medication?',
        [
            'Pain level, respiratory rate, sedation level, and blood pressure; reassess IV route in 15-30 minutes',
            'Temperature and blood pressure only; reassess in 2 hours',
            'Pain level only; reassess when the patient asks for the next dose',
            'Heart rhythm and urine output; reassess in 4 hours',
        ],
        'A',
    ),
    18: (
        'What is the most important safety teaching for a patient taking acetaminophen (Tylenol) along with over-the-counter medicines?',
        [
            'Acetaminophen should always be taken on an empty stomach for best absorption',
            'Many OTC cold and flu medicines already contain acetaminophen, making accidental overdose easy',
            'Acetaminophen can safely be taken in unlimited amounts if you drink plenty of water',
            'Acetaminophen is only dangerous when combined with prescription medications',
        ],
        'B',
    ),
    19: (
        'Which insulin type has the fastest onset of action?',
        [
            'NPH insulin, with onset in 1-2 hours',
            'Regular insulin, with onset in 1-2 hours',
            'Rapid-acting insulin (lispro, aspart), with onset in about 15 minutes',
            'Long-acting insulin (glargine), with onset in about 15 minutes',
        ],
        'C',
    ),
    20: (
        'A patient received rapid-acting insulin, but the meal tray has not arrived. Why is this a concern?',
        [
            'Rapid-acting insulin takes 2-4 hours to work, so the timing does not matter',
            'The insulin will be absorbed too slowly without food in the stomach',
            'The patient may develop hyperglycemia from the stress of not eating',
            'Rapid-acting insulin works in about 15 minutes and can cause hypoglycemia without food',
        ],
        'D',
    ),
    21: (
        'When mixing Regular insulin and NPH insulin in one syringe, which should be drawn up first?',
        [
            'NPH insulin first because it is the longer-acting insulin',
            'Either one can be drawn first as long as the total dose is correct',
            'NPH insulin first because it is cloudy and easier to see in the syringe',
            'Regular insulin first ("clear before cloudy") to prevent contaminating the Regular vial',
        ],
        'D',
    ),
    22: (
        'Which of the following is an early sign of hypoglycemia?',
        [
            'Sweating, shakiness, and fast heartbeat',
            'Fruity-smelling breath and excessive thirst',
            'Flushed dry skin and elevated temperature',
            'Slow bounding pulse and facial swelling',
        ],
        'A',
    ),
    23: (
        "A patient's blood sugar is 62 mg/dL and they are awake and can swallow. What is the correct first step using the Rule of 15?",
        [
            'Give 30 grams of fast-acting sugar and recheck in 30 minutes',
            'Give 15 grams of fast-acting sugar, wait 15 minutes, then recheck blood glucose',
            'Give a full meal with protein and wait 1 hour to recheck',
            'Administer IV dextrose immediately and recheck in 5 minutes',
        ],
        'B',
    ),
    24: (
        'Why is insulin considered a high-alert medication?',
        [
            'Insulin must be refrigerated at all times or it becomes toxic',
            'Insulin can only be administered by a provider, not by a nurse',
            'Even a small dose error can cause dangerous hypoglycemia or hyperglycemia',
            'Insulin requires a separate IV line and cannot be mixed with other fluids',
        ],
        'C',
    ),
    25: (
        "A patient's heart rate is 54 bpm and metoprolol (a beta-blocker) is due. What should you do?",
        [
            'Give the metoprolol and recheck the heart rate in 30 minutes',
            'Give half the ordered dose to reduce the risk of bradycardia',
            'Give the metoprolol with a glass of orange juice to raise the heart rate',
            'Hold the metoprolol, notify the provider, and document your decision',
        ],
        'D',
    ),
    26: (
        "A patient's blood pressure is 88/52 mmHg and their scheduled antihypertensive is due. What should you do?",
        [
            'Give the medication and have the patient lie flat for 30 minutes',
            'Give half the dose and recheck blood pressure in one hour',
            'Give the medication with extra IV fluids to balance the blood pressure',
            'Hold the medication, assess the patient, and notify the provider',
        ],
        'D',
    ),
    27: (
        'A patient on furosemide (Lasix) has a potassium level of 3.1 mEq/L. Which symptoms should the nurse watch for?',
        [
            'Muscle weakness, leg cramps, and irregular heartbeat',
            'Facial flushing, fever, and high blood pressure',
            'Excessive thirst, frequent urination, and weight gain',
            'Joint pain, skin rash, and blurred vision',
        ],
        'A',
    ),
    28: (
        'Which combination of findings is most suggestive of digoxin toxicity?',
        [
            'Hypertension, tachycardia, and increased appetite',
            'Nausea, yellow-green visual halos, and bradycardia',
            'Weight gain, peripheral edema, and elevated potassium',
            'Fever, joint pain, and increased urine output',
        ],
        'B',
    ),
    29: (
        'Which statement correctly matches each anticoagulant with its reversal agent?',
        [
            'Heparin is reversed with vitamin K; warfarin is reversed with protamine sulfate',
            'Both heparin and warfarin are reversed with vitamin K',
            'Heparin is reversed with protamine sulfate; warfarin is reversed with vitamin K',
            'Both heparin and warfarin are reversed with protamine sulfate',
        ],
        'C',
    ),
    30: (
        'A patient on heparin develops new bruising, blood in the urine, and bleeding gums. What should you do FIRST?',
        [
            'Continue the heparin infusion and document the findings',
            'Assess the patient further, then notify the provider immediately',
            'Administer vitamin K to reverse the heparin effects',
            'Increase the IV fluid rate to dilute the heparin concentration',
        ],
        'B',
    ),
    31: (
        'Which of the following is correct teaching for a patient going home on warfarin (Coumadin)?',
        [
            'Avoid all green leafy vegetables completely while taking warfarin',
            'You no longer need regular blood tests once the initial dose is set',
            'Take aspirin freely for headaches since it does not interact with warfarin',
            'Keep vitamin K intake consistent and attend all INR blood test appointments',
        ],
        'D',
    ),
    32: (
        'You have four patients. Which one do you assess FIRST?',
        [
            'A patient on metformin with a blood sugar of 210',
            'A patient on morphine with a respiratory rate of 9',
            'A patient on warfarin with an INR of 2.5',
            'A patient on lisinopril with a dry cough',
        ],
        'B',
    ),
    43: (
        'Furosemide is due but potassium is 3.0 mEq/L. What should you do?',
        [
            'Hold the furosemide, notify the provider, and expect a potassium replacement order',
            'Give the furosemide with a potassium-rich snack like a banana',
            'Give half the furosemide dose to reduce potassium loss',
            'Give the furosemide and recheck potassium in 24 hours',
        ],
        'A',
    ),
    44: (
        'Blood glucose is 62 mg/dL and rapid-acting insulin is due. What should you do?',
        [
            'Give the insulin at a lower dose to prevent further blood sugar drop',
            'Give the insulin and then immediately offer a sugary drink',
            'Hold the insulin, treat the hypoglycemia first, and notify the provider',
            'Give the insulin as ordered since the provider calculated the correct dose',
        ],
        'C',
    ),
    45: (
        'Which combination of symptoms is most characteristic of digoxin toxicity?',
        [
            'Hypertension, tachycardia, and weight gain',
            'Fever, elevated white blood cell count, and cough',
            'Hyperkalemia, muscle cramps, and diarrhea',
            'Nausea, yellow-green visual halos, and bradycardia',
        ],
        'D',
    ),
    46: (
        'A patient is on both heparin and warfarin at the same time. What is the reason for this overlap?',
        [
            'Warfarin takes 3-5 days to reach full effect, so heparin provides immediate protection',
            'Heparin and warfarin must be combined permanently to prevent any clot formation',
            'Warfarin works immediately but heparin is needed to prevent an allergic reaction to it',
            'Both drugs target the same clotting factor and must be given together for full effect',
        ],
        'A',
    ),
    47: (
        'How does ketorolac (Toradol) differ from ibuprofen in clinical use?',
        [
            'Ketorolac is an opioid while ibuprofen is an NSAID',
            'Ketorolac can be given IV/IM and is limited to 5 days due to high bleeding and kidney risk',
            'Ibuprofen is stronger than ketorolac and is limited to 3 days of use',
            'Ketorolac has no risk of GI bleeding because it bypasses the stomach',
        ],
        'B',
    ),
    48: (
        'What is the correct dietary teaching for a patient discharged on warfarin regarding vitamin K?',
        [
            'Avoid all foods containing vitamin K for the duration of treatment',
            'Eat as many green leafy vegetables as possible to boost healthy clotting',
            'Keep vitamin K intake consistent week to week and do not make sudden changes',
            'Take a daily vitamin K supplement to balance out the warfarin effects',
        ],
        'C',
    ),
    49: (
        'A patient on warfarin has an INR of 3.8. What does this result indicate?',
        [
            'The INR is within the normal therapeutic range and no action is needed',
            'The blood is too thick and the warfarin dose should be increased',
            'The patient has a high risk of forming new blood clots',
            'The blood is too thin and the patient has an increased risk of bleeding',
        ],
        'D',
    ),
    50: (
        'Four patients need pain medication. Which one should you assess FIRST?',
        [
            'A patient with pain rated 8/10 and normal vital signs',
            'A patient with mild nausea after taking pain medication',
            'A patient with a respiratory rate of 10 after receiving an opioid',
            'A patient with mild itching after taking pain medication',
        ],
        'C',
    ),
    51: (
        'A patient on an opioid PCA has not pressed the button in 4 hours but is hard to wake. What should you do FIRST?',
        [
            'Assess respiratory rate and oxygen saturation immediately and stop the PCA pump',
            'Press the PCA button for the patient to help manage their pain',
            'Let the patient continue sleeping since they are not requesting medication',
            'Increase the PCA dose since the current setting is clearly not effective',
        ],
        'A',
    ),
    52: (
        'Which set of signs indicates anaphylaxis during a first-dose antibiotic?',
        [
            'Mild rash on the arm, normal blood pressure, and stable breathing',
            'Facial swelling, difficulty breathing, hives, and a sudden drop in blood pressure',
            'Nausea, mild headache, and slight dizziness after the infusion',
            'Elevated temperature, chills, and muscle aches 2 hours later',
        ],
        'B',
    ),
    53: (
        'What should you teach a patient about taking NSAIDs like ibuprofen?',
        [
            'NSAIDs should be taken on an empty stomach for faster absorption',
            'NSAIDs are completely safe for long-term daily use without monitoring',
            'Take NSAIDs with food or a full glass of water to protect the stomach lining',
            'NSAIDs should only be taken at bedtime to reduce daytime drowsiness',
        ],
        'C',
    ),
    54: (
        'A nurse is comparing morphine and hydromorphone (Dilaudid). Which statement is correct about their relative strength?',
        [
            'Morphine and hydromorphone are equal in strength milligram for milligram',
            'Morphine is much stronger than hydromorphone per milligram',
            'Hydromorphone is weaker than morphine and requires larger doses for the same effect',
            'Hydromorphone is much stronger — 1 mg equals roughly 5-7 mg of morphine',
        ],
        'D',
    ),
    55: (
        'A patient with chronic pain asks to increase their opioid dose. The provider orders multimodal pain management instead. What is the main benefit of this approach?',
        [
            'It uses multiple pain treatments together, allowing lower opioid doses with better overall control',
            'It replaces all medications with non-drug therapies like ice and relaxation only',
            'It increases the opioid dose gradually while adding a muscle relaxant for extra relief',
            'It eliminates the need for any follow-up pain assessments after discharge',
        ],
        'A',
    ),
    56: (
        'Which of the following correctly describes the Rule of 15 for treating hypoglycemia in a conscious patient?',
        [
            'Give 5 grams of sugar, wait 5 minutes, and recheck blood glucose',
            'Give 30 grams of sugar, wait 30 minutes, then provide a full meal',
            'Give 50 mL of IV dextrose, wait 10 minutes, then give glucagon IM',
            'Give 15 grams of fast-acting sugar, wait 15 minutes, and recheck blood glucose',
        ],
        'D',
    ),
    57: (
        "A patient on heparin has platelets dropping from 180,000 to 85,000 over 5 days. What is the most likely concern?",
        [
            'Heparin-induced thrombocytopenia (HIT), which requires stopping all heparin immediately',
            'A normal expected response to heparin therapy that requires no intervention',
            'Iron deficiency anemia caused by the heparin infusion',
            'An allergic skin reaction that is treated by reducing the heparin dose',
        ],
        'A',
    ),
}


def main():
    with open(FILEPATH, 'r') as f:
        content = f.read()

    # Extract Exam #1 section
    exam_start = content.index('## Exam #1')
    section = content[exam_start:]
    lines = section.split('\n')

    # Find card start line indices
    card_start_indices = []
    for i, line in enumerate(lines):
        if re.match(r'### Card \d+', line):
            card_start_indices.append(i)

    # Extract individual card texts
    cards_raw = []
    for idx, start in enumerate(card_start_indices):
        end = card_start_indices[idx + 1] if idx + 1 < len(card_start_indices) else len(lines)
        card_text = '\n'.join(lines[start:end])
        cards_raw.append(card_text)

    # Print section header
    print('## Exam #1')
    print()

    for idx, card_text in enumerate(cards_raw):
        num = int(re.search(r'### Card (\d+)', card_text).group(1))
        header = re.search(r'### Card \d+ \([^)]+\)', card_text).group(0)

        front_text, options, correct = CARD_DATA[num]

        # Extract content after **Back:**\n
        back_match = re.search(r'\*\*Back:\*\*\n', card_text)
        after_back = card_text[back_match.end():].rstrip('\n')

        # Print the card
        print(header)
        print()
        print(f'**Front:** {front_text}')
        print()
        print(f'A. {options[0]}  ')
        print(f'B. {options[1]}  ')
        print(f'C. {options[2]}  ')
        print(f'D. {options[3]}  ')
        print()
        print('**Back:**')
        print(f'**Correct answer: {correct}**')
        print()
        print(after_back)

        if idx < len(cards_raw) - 1:
            print()


if __name__ == '__main__':
    main()
