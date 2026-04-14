#!/usr/bin/env python3
"""Generate MCQ options for Pharmacologic Principles section (Cards 1-11, 33-42)."""

import re

SOURCE = "/Users/cornelius/Desktop/code/flashcards/data/pharmacology/exam-1/exam-1-flashcards.md"

# Card data: card_number -> { front (optional rephrase), correct, options }
CARDS = {
    1: {
        "front": "A patient gets a new drug and feels a little dizzy. A different patient gets the same drug and breaks out in hives with facial swelling. Which reaction requires the fastest nursing action?",
        "correct": "C",
        "options": [
            "A. The dizziness, because it is a sign of drug toxicity requiring immediate intervention",
            "B. Both reactions require the same urgency since they are both adverse effects",
            "C. The hives with facial swelling, because it is an adverse effect requiring the nurse to stop the drug and get help",
            "D. Neither reaction is urgent because both are expected side effects of the medication",
        ],
    },
    2: {
        "front": "A nurse gives morphine (an opioid agonist) for pain. Later, the patient's breathing slows dangerously, and the nurse gives naloxone. Which statement best describes how an agonist and antagonist work?",
        "correct": "A",
        "options": [
            "A. An agonist activates a receptor to produce a response, while an antagonist blocks a receptor to stop a response",
            "B. An agonist blocks a receptor to prevent side effects, while an antagonist activates a receptor to reverse toxicity",
            "C. Both agonists and antagonists activate receptors, but antagonists produce a weaker response",
            "D. An agonist works only on pain receptors, while an antagonist works only on breathing receptors",
        ],
    },
    3: {
        "front": None,  # keep original
        "correct": "B",
        "options": [
            "A. IV drugs are formulated at a higher concentration than oral drugs",
            "B. IV drugs enter the bloodstream directly, skipping absorption and first-pass metabolism in the liver",
            "C. IV drugs are absorbed faster through the stomach lining than oral drugs",
            "D. IV drugs bind to proteins more quickly, which speeds up their effect",
        ],
    },
    4: {
        "front": "A patient who takes an oral heart medication starts having vomiting and diarrhea. The nurse notices the drug seems less effective. Which of the following best explains why?",
        "correct": "D",
        "options": [
            "A. The patient has developed tolerance to the medication and needs a higher dose",
            "B. The drug has reached toxic levels and is being rejected by the body",
            "C. The vomiting and diarrhea are adverse effects indicating the drug should be discontinued",
            "D. The vomiting and diarrhea are preventing the drug from staying in the GI tract long enough to be absorbed",
        ],
    },
    5: {
        "front": None,
        "correct": "C",
        "options": [
            "A. Sublingual tablets contain a higher dose of the drug than oral tablets",
            "B. Sublingual drugs are absorbed faster because the stomach breaks them down more efficiently",
            "C. Sublingual drugs absorb through the tissues under the tongue directly into the blood, skipping the stomach and liver",
            "D. Sublingual drugs work faster because saliva activates the medication before it enters the body",
        ],
    },
    6: {
        "front": None,
        "correct": "A",
        "options": [
            "A. Low albumin means more of the drug is free and active in the blood, increasing the risk of a stronger effect and toxicity",
            "B. Low albumin causes the drug to be excreted too quickly by the kidneys, leading to a rebound toxic effect",
            "C. Low albumin prevents the drug from reaching its target receptor, so the provider increases the dose to a toxic level",
            "D. Low albumin causes the liver to metabolize the drug faster, producing toxic byproducts",
        ],
    },
    7: {
        "front": None,
        "correct": "D",
        "options": [
            "A. The drug will be excreted unchanged by the kidneys, so no dose adjustment is needed",
            "B. The drug will be metabolized faster than normal, requiring higher doses to be effective",
            "C. The drug will bind to more albumin than usual, reducing its effect and requiring a higher dose",
            "D. The drug may build up to dangerous levels because the liver cannot break it down normally, increasing toxicity risk",
        ],
    },
    8: {
        "front": None,
        "correct": "B",
        "options": [
            "A. Grapefruit juice speeds up drug metabolism, making the statin less effective over time",
            "B. Grapefruit juice blocks liver enzymes that break down the drug, causing blood levels to rise and increasing toxicity risk",
            "C. Grapefruit juice interferes with drug absorption in the stomach, so the statin should be taken two hours apart",
            "D. Grapefruit juice has no significant effect on statins but should be avoided due to its high sugar content",
        ],
    },
    9: {
        "front": "A patient is taking Drug A. A new Drug B is added that inhibits the metabolism of Drug A. What effect should the nurse expect?",
        "correct": "C",
        "options": [
            "A. Drug A will be broken down faster, leading to lower blood levels and a weaker therapeutic effect",
            "B. Drug A will be excreted more quickly by the kidneys, requiring a higher dose to remain effective",
            "C. Drug A will be broken down more slowly, causing higher blood levels and an increased risk of toxicity",
            "D. Drug A will bind to fewer proteins, reducing its effect and requiring a dose increase",
        ],
    },
    10: {
        "front": "Before scanning a patient's wristband and giving a medication, which of the following is included in the rights of medication administration?",
        "correct": "D",
        "options": [
            "A. Right patient, right drug, right dose, and right diagnosis",
            "B. Right patient, right drug, right dose, and right pharmacy",
            "C. Right patient, right drug, right cost, and right time",
            "D. Right patient, right drug, right dose, right route, right time, and right documentation",
        ],
    },
    11: {
        "front": "You are about to give a medication you have not given before. Which question is MOST important to ask yourself first?",
        "correct": "A",
        "options": [
            'A. "What assessment or lab should I check first, and is this drug safe for this patient right now?"',
            'B. "Has this drug been given to other patients on the unit today without any problems?"',
            'C. "Is this medication available in the automated dispensing machine on my floor?"',
            'D. "What is the cost of this drug compared to other options the provider could have ordered?"',
        ],
    },
    33: {
        "front": None,
        "correct": "D",
        "options": [
            "A. The drug will be metabolized faster by the liver to compensate for the kidney failure",
            "B. The drug will have a weaker effect because kidney failure reduces drug activation",
            "C. The drug will be absorbed more slowly from the GI tract, delaying its onset of action",
            "D. The drug may build up in the body because the kidneys cannot clear it normally, increasing the risk of toxicity",
        ],
    },
    34: {
        "front": "A nurse gives a patient IV pain medication. When should the nurse plan to reassess the patient's pain level?",
        "correct": "B",
        "options": [
            "A. Within 5 minutes, because IV drugs always reach full effect immediately",
            "B. Within 15 to 30 minutes, because IV drugs have a fast onset compared to oral drugs",
            "C. Within 60 to 90 minutes, because all pain medications take at least one hour to work",
            "D. Only after the next scheduled dose, because reassessing too soon gives inaccurate results",
        ],
    },
    35: {
        "front": None,
        "correct": "C",
        "options": [
            "A. The new drug will speed up metabolism of the other drugs, causing them to become less effective",
            "B. The new drug will block absorption of the other drugs in the GI tract, reducing their blood levels",
            "C. The new drug will slow the breakdown of the other drugs, raising their blood levels and increasing toxicity risk",
            "D. The new drug will increase kidney excretion of the other drugs, requiring higher doses to maintain effect",
        ],
    },
    36: {
        "front": "A patient asks why they cannot crush their extended-release pain tablet to make it easier to swallow. What is the nurse's best response?",
        "correct": "D",
        "options": [
            'A. "Crushing the tablet makes it taste very bitter and reduces patient satisfaction with the medication."',
            'B. "Crushing the tablet destroys the active ingredient so the drug will have no effect at all."',
            'C. "Crushing the tablet changes the color of the medication, making it harder to identify correctly."',
            'D. "Crushing the tablet releases the full dose at once instead of slowly over time, which could cause a dangerous overdose."',
        ],
    },
    37: {
        "front": None,
        "correct": "A",
        "options": [
            "A. Poor blood flow to the tissues in shock prevents the SubQ drug from being absorbed into the bloodstream",
            "B. SubQ injections are always ineffective for emergency medications regardless of the patient's condition",
            "C. The drug was destroyed by enzymes in the subcutaneous tissue before it could be absorbed",
            "D. The patient developed an immune response to the SubQ injection site, blocking drug absorption",
        ],
    },
    38: {
        "front": None,
        "correct": "D",
        "options": [
            "A. Serum albumin and total protein levels",
            "B. ALT and AST liver enzyme levels",
            "C. Complete blood count (CBC) and platelet count",
            "D. Serum creatinine and BUN (blood urea nitrogen)",
        ],
    },
    39: {
        "front": None,
        "correct": "B",
        "options": [
            "A. A loading dose is a smaller test dose given first to check for allergies, and a maintenance dose is the full regular dose",
            "B. A loading dose is a higher first dose to quickly reach a therapeutic blood level, and a maintenance dose is a smaller regular dose to keep the level steady",
            "C. A loading dose is given only by IV, and a maintenance dose is always given by mouth",
            "D. A loading dose and maintenance dose are the same amount, but given at different times of day",
        ],
    },
    40: {
        "front": None,
        "correct": "C",
        "options": [
            "A. The drug must be given by IV only, which increases the risk of infection at the injection site",
            "B. The drug cannot be taken with any food or other medications, making dosing very difficult",
            "C. The difference between the dose that helps and the dose that harms is very small, so even minor changes can cause toxicity",
            "D. The drug has a very long half-life, meaning it takes weeks to reach a steady blood level",
        ],
    },
    41: {
        "front": None,
        "correct": "A",
        "options": [
            "A. The drugs compete for binding sites on albumin, which can increase the free amount of one drug and raise the risk of toxicity",
            "B. The drugs bind to each other in the bloodstream, forming an inactive compound that is excreted by the kidneys",
            "C. The drugs both bind to albumin without affecting each other because there are enough binding sites for both",
            "D. The drugs cancel each other out, resulting in neither drug producing its intended therapeutic effect",
        ],
    },
    42: {
        "front": "A patient asks \"Why do I need blood tests for this medicine?\" Which is the best explanation of therapeutic drug monitoring?",
        "correct": "B",
        "options": [
            'A. "The blood tests check if you are allergic to the medication so we can switch to a different one if needed."',
            'B. "The blood tests make sure your drug level is in the safe and effective range — not too low and not too high."',
            'C. "The blood tests are required by the pharmacy before they will refill your prescription each month."',
            'D. "The blood tests measure how fast your body absorbs the drug so we can change the time you take it."',
        ],
    },
}


def process():
    with open(SOURCE, "r") as f:
        lines = f.readlines()

    # Find the "## Exam #1" line
    cutoff = None
    for i, line in enumerate(lines):
        if line.strip() == "## Exam #1":
            cutoff = i
            break
    if cutoff is None:
        raise ValueError("Could not find '## Exam #1' heading")

    section_lines = lines[:cutoff]
    text = "".join(section_lines)

    # Split into cards using ### Card N pattern
    # We'll process by finding each card block
    card_pattern = re.compile(r"^### Card (\d+) \(", re.MULTILINE)
    matches = list(card_pattern.finditer(text))

    result_parts = []
    # Text before first card
    if matches:
        result_parts.append(text[: matches[0].start()])

    for idx, match in enumerate(matches):
        card_num = int(match.group(1))
        # Get the card text
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        card_text = text[start:end]

        if card_num in CARDS:
            card_data = CARDS[card_num]
            # Find Front and Back lines
            front_match = re.search(
                r"(\*\*Front:\*\* )(.*?)(\n)", card_text
            )
            back_match = re.search(r"(\*\*Back:\*\*\n)", card_text)

            if front_match and back_match:
                # Build new front line
                if card_data["front"]:
                    new_front_line = f"**Front:** {card_data['front']}\n"
                else:
                    new_front_line = front_match.group(0)

                # Build options block
                options_block = "\n"
                for opt in card_data["options"]:
                    options_block += f"{opt}  \n"
                options_block += "\n"

                # Build new back line with correct answer
                new_back = f"**Back:**\n**Correct answer: {card_data['correct']}**\n"

                # Reconstruct card
                before_front = card_text[: front_match.start()]
                after_front_before_back = card_text[
                    front_match.end() : back_match.start()
                ]
                after_back = card_text[back_match.end() :]

                card_text = (
                    before_front
                    + new_front_line
                    + options_block
                    + new_back
                    + after_back
                )

        result_parts.append(card_text)

    output = "".join(result_parts)
    # Ensure it ends with a single newline
    output = output.rstrip("\n") + "\n"
    print(output)


if __name__ == "__main__":
    process()
