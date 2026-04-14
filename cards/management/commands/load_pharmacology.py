"""
Management command to load pharmacology data from markdown files in data/pharmacology/.

Loads guides, flashcards (concept), and application questions for:
  anti-infectives, anticoagulants, cardiac, psych, seizure-electrolytes
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from cards.models import Category, Deck, Card, GuideSection


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "pharmacology"

DECKS = [
    {"slug": "exam-1", "name": "Exam 1", "order": 1},
    {"slug": "exam-2", "name": "Exam 2", "order": 2},
    {"slug": "anti-infectives", "name": "Anti-Infectives", "order": 3},
    {"slug": "anticoagulants", "name": "Anticoagulants", "order": 4},
    {"slug": "cardiac", "name": "Cardiac Medications", "order": 5},
    {"slug": "psych", "name": "Psych Medications", "order": 6},
    {"slug": "seizure-electrolytes", "name": "Seizure & Electrolytes", "order": 7},
]

# Guide headings to skip (non-content sections)
SKIP_GUIDE_HEADINGS = {
    "table of contents",
    "how to use this guide",
    "how this guide is organized",
}


def _strip_emoji(text):
    """Remove common emoji/icon prefixes from headings."""
    return re.sub(r"^[\U0001f300-\U0001faff\u2600-\u27bf\u200d\ufe0f📋📖🧠💊🚨\s]+", "", text).strip()


def _clean_text(text):
    """Strip leading/trailing whitespace and blank lines."""
    lines = text.strip().splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


# ── Guide parsing ─────────────────────────────────


def parse_guide(filepath):
    """Parse a guide markdown file into (title, content) sections."""
    text = filepath.read_text(encoding="utf-8")
    # Split on ## headings (not ### which are sub-sections within a guide section)
    parts = re.split(r"^(## .+)$", text, flags=re.MULTILINE)

    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].lstrip("# ").strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""

        clean_heading = _strip_emoji(heading).strip()
        if clean_heading.lower() in SKIP_GUIDE_HEADINGS:
            continue
        # Skip numbered prefix like "1. " from title for cleanliness
        title = re.sub(r"^\d+\.\s*", "", clean_heading).strip()
        if not title:
            continue

        content = _clean_text(content)
        if content:
            sections.append((title, content))

    return sections


# ── Flashcard parsing ─────────────────────────────


def _split_by_card_heading(text):
    """Split text into blocks by Card/Flashcard headings (## or ###)."""
    pattern = r"^#{2,3}\s+(?:Card|Flashcard)\s+\d+"
    parts = re.split(f"({pattern}.*)", text, flags=re.MULTILINE)
    blocks = []
    for i in range(1, len(parts), 2):
        heading = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        blocks.append(heading + "\n" + body)
    return blocks


def _extract_details_content(block):
    """Extract text inside <details>...</details> tags."""
    match = re.search(r"<details>.*?<summary>.*?</summary>(.*?)</details>", block, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def parse_flashcard_front_back(block):
    """Parse a flashcard with **Front:**/**Back:**/**Why it matters:** format."""
    front_match = re.search(r"\*\*Front:\*\*\s*(.*?)(?=\n\*\*Back:\*\*)", block, re.DOTALL)
    back_match = re.search(r"\*\*Back:\*\*\s*(.*?)(?=\n\*\*Why it matters:\*\*)", block, re.DOTALL)
    why_match = re.search(r"\*\*Why it matters:\*\*\s*(.*?)(?=\n---|\Z)", block, re.DOTALL)

    if not front_match or not back_match:
        return None
    question = _clean_text(front_match.group(1))
    answer = _clean_text(back_match.group(1))
    rationale = _clean_text(why_match.group(1)) if why_match else ""
    return question, answer, rationale


def parse_flashcard_q_details(block):
    """Parse a flashcard with **Q:** and <details> answer format."""
    q_match = re.search(r"\*\*Q:\s*(.*?)\*\*", block, re.DOTALL)
    if not q_match:
        return None

    question_stem = _clean_text(q_match.group(1))

    # Capture A-D options between the Q line and <details>
    after_q = block[q_match.end():]
    before_details = re.split(r"<details>", after_q, maxsplit=1)[0]
    options_text = _clean_text(before_details)

    if options_text:
        question = question_stem + "\n\n" + options_text
    else:
        question = question_stem

    details = _extract_details_content(block)
    if not details:
        return None

    answer = _clean_text(details)
    rationale = ""

    return question, answer, rationale


def parse_flashcards(filepath):
    """Parse a flashcards markdown file into (question, answer, rationale) tuples."""
    text = filepath.read_text(encoding="utf-8")
    blocks = _split_by_card_heading(text)
    cards = []
    for block in blocks:
        result = parse_flashcard_front_back(block)
        if not result:
            result = parse_flashcard_q_details(block)
        if result:
            q, a, r = result
            if q and a:
                cards.append((q, a, r))
    return cards


# ── Application question parsing ──────────────────


def _split_by_question_heading(text):
    """Split text into blocks by Question headings (## or ###)."""
    pattern = r"^#{2,3}\s+Question\s+\d+"
    parts = re.split(f"({pattern}.*)", text, flags=re.MULTILINE)
    blocks = []
    for i in range(1, len(parts), 2):
        heading = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        blocks.append(heading + "\n" + body)
    return blocks


def parse_app_question_standard(block):
    """Parse app question with **Correct Answer(s): X** format."""
    # Match both single answer and SATA (multiple answers)
    match = re.search(r"\*\*Correct Answers?:\s*([A-F](?:,\s*[A-F])*)\*\*", block)
    if not match:
        return None
    correct_letters = match.group(1)

    # Question = everything from first non-heading line to the correct answer line
    lines = block.split("\n")
    q_lines = []
    started = False
    for line in lines:
        if re.match(r"^#{2,3}\s+Question", line):
            continue
        if "**Correct Answer" in line:
            break
        if line.strip().startswith("---"):
            continue
        if not started and not line.strip():
            continue
        started = True
        q_lines.append(line)
    question = _clean_text("\n".join(q_lines))

    answer = f"Correct: {correct_letters}"

    # Extract explanation
    explanation = ""
    # Try <details> first
    details = _extract_details_content(block)
    if details:
        explanation = _clean_text(details)
    else:
        # Try **Explanation:** block
        expl_match = re.search(r"\*\*Explanation:\*\*\s*(.*?)(?=\n---|\Z)", block, re.DOTALL)
        if expl_match:
            explanation = _clean_text(expl_match.group(1))
        else:
            # Everything after the Correct Answer(s) line
            after_match = re.search(r"\*\*Correct Answers?:.*?\*\*\s*\n(.*?)(?=\n---|\Z)", block, re.DOTALL)
            if after_match:
                explanation = _clean_text(after_match.group(1))

    return question, answer, explanation


def parse_app_question_details(block):
    """Parse app question with answer inside <details> (psych/seizure format)."""
    details = _extract_details_content(block)
    if not details:
        return None

    # Look for ✅ pattern in details
    correct_match = re.search(r"\*\*✅\s*(?:Correct:\s*)?([A-D])[\.\)\s—–-]*(.+?)\*\*", details)
    if not correct_match:
        return None

    correct_letter = correct_match.group(1)

    # Question = everything from start to <details>
    lines = block.split("\n")
    q_lines = []
    started = False
    for line in lines:
        if re.match(r"^#{2,3}\s+Question", line):
            continue
        if "<details>" in line:
            break
        if line.strip().startswith("---"):
            continue
        if not started and not line.strip():
            continue
        started = True
        q_lines.append(line)
    question = _clean_text("\n".join(q_lines))

    answer = f"Correct: {correct_letter}"
    explanation = _clean_text(details)

    return question, answer, explanation


def parse_app_questions(filepath):
    """Parse an application questions markdown file."""
    text = filepath.read_text(encoding="utf-8")
    blocks = _split_by_question_heading(text)
    cards = []
    for block in blocks:
        result = parse_app_question_standard(block)
        if not result:
            result = parse_app_question_details(block)
        if result:
            q, a, r = result
            if q and a:
                cards.append((q, a, r))
    return cards


# ── Command ───────────────────────────────────────


class Command(BaseCommand):
    help = "Load pharmacology deck data from markdown files in data/pharmacology/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data for target decks before loading",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report counts without writing to DB",
        )

    def handle(self, *args, **options):
        target_slugs = [d["slug"] for d in DECKS]

        category = Category.objects.filter(slug="pharmacology").first()
        if not category:
            self.stderr.write("Pharmacology category not found. Run seed_cards first.")
            return

        if options["clear"]:
            self._clear_decks(category, target_slugs)

        total_cards = 0
        total_guides = 0

        for deck_info in DECKS:
            slug = deck_info["slug"]
            deck_dir = DATA_DIR / slug
            if not deck_dir.is_dir():
                self.stderr.write(f"  ⚠ Directory not found: {deck_dir}")
                continue

            guide_file = deck_dir / f"{slug}-guide.md"
            flash_file = deck_dir / f"{slug}-flashcards.md"
            app_file = deck_dir / f"{slug}-application-questions.md"

            # Parse all files first
            guide_sections = parse_guide(guide_file) if guide_file.exists() else []
            flashcards = parse_flashcards(flash_file) if flash_file.exists() else []
            app_questions = parse_app_questions(app_file) if app_file.exists() else []

            self.stdout.write(
                f"\n{'─' * 40}\n"
                f"  {deck_info['name']} ({slug})\n"
                f"  Guide sections: {len(guide_sections)}\n"
                f"  Flashcards:     {len(flashcards)}\n"
                f"  App questions:  {len(app_questions)}\n"
            )

            if options["dry_run"]:
                total_cards += len(flashcards) + len(app_questions)
                total_guides += len(guide_sections)
                continue

            with transaction.atomic():
                deck, created = Deck.objects.get_or_create(
                    category=category,
                    slug=slug,
                    defaults={
                        "name": deck_info["name"],
                        "order": deck_info["order"],
                    },
                )
                if created:
                    self.stdout.write(f"  Created deck: {deck}")
                else:
                    self.stdout.write(f"  Deck exists: {deck}")

                # Load guide sections
                gs_count = 0
                for order, (title, content) in enumerate(guide_sections, start=1):
                    _, gs_created = GuideSection.objects.get_or_create(
                        deck=deck,
                        title=title,
                        defaults={"content": content, "order": order},
                    )
                    if gs_created:
                        gs_count += 1
                total_guides += gs_count
                self.stdout.write(f"  → {gs_count} guide sections created")

                # Load flashcards — auto-detect type based on presence of choices
                fc_count = 0
                for q, a, r in flashcards:
                    has_choices = bool(
                        re.search(r"\nA[\.\)]", q) or re.search(r"\n- A[\.\)]", q)
                    )
                    qtype = Card.APPLICATION if has_choices else Card.CONCEPT
                    _, c_created = Card.objects.get_or_create(
                        category=category,
                        deck=deck,
                        question=q,
                        question_type=qtype,
                        defaults={
                            "answer": a,
                            "rationale": r,
                            "is_default": True,
                        },
                    )
                    if c_created:
                        fc_count += 1
                total_cards += fc_count
                self.stdout.write(f"  → {fc_count} flashcards created")

                # Load app questions
                aq_count = 0
                for q, a, r in app_questions:
                    _, c_created = Card.objects.get_or_create(
                        category=category,
                        deck=deck,
                        question=q,
                        question_type=Card.APPLICATION,
                        defaults={
                            "answer": a,
                            "rationale": r,
                            "is_default": True,
                        },
                    )
                    if c_created:
                        aq_count += 1
                total_cards += aq_count
                self.stdout.write(f"  → {aq_count} application cards created")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! {total_cards} cards, {total_guides} guide sections."
            )
        )

    def _clear_decks(self, category, slugs):
        """Delete cards, guide sections, and decks for the target slugs."""
        decks = Deck.objects.filter(category=category, slug__in=slugs)
        card_count = Card.objects.filter(deck__in=decks).delete()[0]
        gs_count = GuideSection.objects.filter(deck__in=decks).delete()[0]
        deck_count = decks.delete()[0]
        self.stdout.write(
            f"Cleared: {card_count} cards, {gs_count} guide sections, "
            f"{deck_count} decks"
        )
