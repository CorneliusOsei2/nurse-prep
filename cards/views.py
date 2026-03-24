import json
import random
from datetime import date, timedelta

import markdown as md_lib
from django.db.models import Count, Q, Avg
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CardForm, CategoryForm, ImportForm
from .models import (
    Category, Deck, GuideSection, Card, Progress,
    StudySession, Quiz, QuizQuestion, GuideSectionProgress,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXCLUDED_GUIDE_PREFIXES = ('How to use', 'Best way', 'Fast Final')


def _topic_queryset():
    """GuideSections that represent real topics (not meta sections)."""
    qs = GuideSection.objects.all()
    for prefix in EXCLUDED_GUIDE_PREFIXES:
        qs = qs.exclude(title__istartswith=prefix)
    return qs


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def dashboard_view(request):
    categories = Category.objects.filter(published=True).annotate(
        card_count=Count('cards'),
        deck_count=Count('decks'),
    )

    # Compute progress per category
    for cat in categories:
        total = cat.card_count
        studied = Progress.objects.filter(card__category=cat, times_studied__gt=0).count()
        cat.progress_pct = round(studied / total * 100) if total else 0

    recent_quizzes = Quiz.objects.filter(completed_at__isnull=False)[:5]

    return render(request, 'cards/dashboard.html', {
        'categories': categories,
        'recent_quizzes': recent_quizzes,
    })


# ---------------------------------------------------------------------------
# Category & Exam Hub
# ---------------------------------------------------------------------------

def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    decks = category.decks.annotate(
        card_count=Count('cards'),
        has_guide=Count('guide_sections'),
    )
    return render(request, 'cards/category_detail.html', {
        'category': category,
        'decks': decks,
    })


def exam_detail_view(request, slug, deck_id):
    category = get_object_or_404(Category, slug=slug)
    deck = get_object_or_404(Deck, pk=deck_id, category=category)
    sections = deck.guide_sections.all()

    # Attach completion progress to each section
    for section in sections:
        prog, _ = GuideSectionProgress.objects.get_or_create(section=section)
        section.is_completed = prog.completed

    return render(request, 'cards/exam_detail.html', {
        'category': category,
        'deck': deck,
        'sections': sections,
    })


# ---------------------------------------------------------------------------
# Learn
# ---------------------------------------------------------------------------

def learn_view(request, slug, deck_id):
    category = get_object_or_404(Category, slug=slug)
    deck = get_object_or_404(Deck, pk=deck_id, category=category)
    sections = deck.guide_sections.all()

    total = sections.count()
    completed = 0

    rendered_sections = []
    for section in sections:
        prog, _ = GuideSectionProgress.objects.get_or_create(section=section)
        html_content = md_lib.markdown(section.content, extensions=['extra', 'nl2br'])
        rendered_sections.append({
            'id': section.id,
            'title': section.title,
            'html': html_content,
            'completed': prog.completed,
        })
        if prog.completed:
            completed += 1

    progress_pct = round(completed / total * 100) if total else 0

    return render(request, 'cards/learn.html', {
        'category': category,
        'deck': deck,
        'sections': rendered_sections,
        'progress_pct': progress_pct,
        'completed_count': completed,
        'total_count': total,
    })


# ---------------------------------------------------------------------------
# Study (Flashcards)
# ---------------------------------------------------------------------------

def study_view(request):
    categories = Category.objects.filter(published=True).annotate(
        card_count=Count('cards'),
    )

    topics = _topic_queryset().annotate(
        card_count=Count('cards'),
    ).select_related('deck', 'deck__category')

    return render(request, 'cards/study.html', {
        'categories': categories,
        'topics': topics,
    })


# ---------------------------------------------------------------------------
# Quiz / Test
# ---------------------------------------------------------------------------

def quiz_setup_view(request):
    topics = _topic_queryset().annotate(
        card_count=Count('cards'),
    ).select_related('deck', 'deck__category')

    return render(request, 'cards/quiz_setup.html', {
        'topics': topics,
    })


@csrf_exempt
@require_POST
def quiz_start_view(request):
    category_id = request.POST.get('category')
    deck_id = request.POST.get('deck')
    section_ids = request.POST.get('section', '')
    num_questions = int(request.POST.get('num_questions', 20))
    time_limit = request.POST.get('time_limit')

    cards = Card.objects.all()

    if category_id:
        cards = cards.filter(category_id=category_id)
    if deck_id:
        cards = cards.filter(deck_id=deck_id)
    if section_ids:
        ids = [int(x) for x in section_ids.split(',') if x.strip()]
        if ids:
            cards = cards.filter(guide_section_id__in=ids)

    card_list = list(cards)
    random.shuffle(card_list)
    selected = card_list[:num_questions]

    quiz = Quiz.objects.create(
        category_id=category_id if category_id else None,
        num_questions=len(selected),
        time_limit=int(time_limit) if time_limit else None,
    )

    for i, card in enumerate(selected):
        QuizQuestion.objects.create(quiz=quiz, card=card, order=i + 1)

    return redirect('cards:quiz_play', pk=quiz.pk)


def quiz_play_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.select_related('card')
    return render(request, 'cards/quiz_play.html', {
        'quiz': quiz,
        'questions': questions,
    })


def quiz_results_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.select_related('card')
    return render(request, 'cards/quiz_results.html', {
        'quiz': quiz,
        'questions': questions,
    })


def quiz_history_view(request):
    quizzes = Quiz.objects.filter(completed_at__isnull=False)
    return render(request, 'cards/quiz_history.html', {
        'quizzes': quizzes,
    })


# ---------------------------------------------------------------------------
# Card Management
# ---------------------------------------------------------------------------

def manage_view(request):
    cards = Card.objects.select_related('category', 'deck').all()
    return render(request, 'cards/manage.html', {'cards': cards})


def card_create_view(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cards:manage')
    else:
        form = CardForm()
    return render(request, 'cards/card_form.html', {'form': form, 'title': 'Add Card'})


def card_edit_view(request, pk):
    card = get_object_or_404(Card, pk=pk)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('cards:manage')
    else:
        form = CardForm(instance=card)
    return render(request, 'cards/card_form.html', {'form': form, 'title': 'Edit Card'})


def card_delete_view(request, pk):
    card = get_object_or_404(Card, pk=pk)
    if request.method == 'POST':
        card.delete()
        return redirect('cards:manage')
    return render(request, 'cards/card_confirm_delete.html', {'card': card})


def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cards:manage')
    else:
        form = CategoryForm()
    return render(request, 'cards/category_form.html', {'form': form})


def import_cards_view(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            data = json.load(request.FILES['file'])
            cards_data = data if isinstance(data, list) else data.get('cards', [])
            for item in cards_data:
                cat, _ = Category.objects.get_or_create(
                    name=item.get('category', 'Imported'),
                    defaults={'slug': item.get('category', 'imported').lower().replace(' ', '-')},
                )
                deck = None
                if item.get('deck'):
                    deck, _ = Deck.objects.get_or_create(
                        category=cat,
                        name=item['deck'],
                        defaults={'slug': item['deck'].lower().replace(' ', '-')},
                    )
                Card.objects.create(
                    category=cat,
                    deck=deck,
                    question=item.get('question', ''),
                    answer=item.get('answer', ''),
                    rationale=item.get('rationale', ''),
                )
            return redirect('cards:manage')
    else:
        form = ImportForm()
    return render(request, 'cards/import.html', {'form': form})


# ---------------------------------------------------------------------------
# API — Cards
# ---------------------------------------------------------------------------

def api_cards(request):
    cards = Card.objects.select_related('category', 'deck', 'guide_section')
    category = request.GET.get('category')
    deck = request.GET.get('deck')
    section = request.GET.get('section')

    if category:
        cards = cards.filter(category_id=category)
    if deck:
        cards = cards.filter(deck_id=deck)
    if section:
        ids = [int(x) for x in section.split(',') if x.strip()]
        if ids:
            cards = cards.filter(guide_section_id__in=ids)

    result = []
    for card in cards:
        progress = getattr(card, 'progress', None)
        result.append({
            'id': card.id,
            'question': card.question,
            'answer': card.answer,
            'rationale': card.rationale,
            'category': card.category.name if card.category else None,
            'deck': card.deck.name if card.deck else None,
            'guide_section': card.guide_section.title if card.guide_section else None,
            'ease_factor': progress.ease_factor if progress else 2.5,
            'interval': progress.interval if progress else 0,
            'repetitions': progress.repetitions if progress else 0,
            'times_studied': progress.times_studied if progress else 0,
            'last_rating': progress.last_rating if progress else 0,
        })

    return JsonResponse(result, safe=False)


# ---------------------------------------------------------------------------
# API — Rate Card (SM-2)
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def api_rate_card(request, pk):
    card = get_object_or_404(Card, pk=pk)
    data = json.loads(request.body)
    quality = int(data.get('quality', 0))  # 0-5

    progress, _ = Progress.objects.get_or_create(card=card)

    # SM-2 algorithm
    if quality >= 3:
        if progress.repetitions == 0:
            progress.interval = 1
        elif progress.repetitions == 1:
            progress.interval = 6
        else:
            progress.interval = round(progress.interval * progress.ease_factor)
        progress.repetitions += 1
    else:
        progress.repetitions = 0
        progress.interval = 1

    progress.ease_factor = max(
        1.3,
        progress.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    progress.times_studied += 1
    progress.last_rating = quality
    progress.next_review = date.today() + timedelta(days=progress.interval)
    progress.save()

    # Update study session
    session, _ = StudySession.objects.get_or_create(date=date.today())
    session.cards_studied += 1
    if quality >= 3:
        session.cards_correct += 1
    session.save()

    return JsonResponse({
        'ease_factor': progress.ease_factor,
        'interval': progress.interval,
        'repetitions': progress.repetitions,
        'next_review': str(progress.next_review),
    })


# ---------------------------------------------------------------------------
# API — Stats
# ---------------------------------------------------------------------------

def api_stats(request):
    total_cards = Card.objects.count()
    studied = Progress.objects.filter(times_studied__gt=0).count()
    mastered = Progress.objects.filter(repetitions__gte=3).count()

    sessions = StudySession.objects.all()[:7]
    session_data = [
        {'date': str(s.date), 'studied': s.cards_studied, 'correct': s.cards_correct}
        for s in sessions
    ]

    avg_ease = Progress.objects.filter(times_studied__gt=0).aggregate(
        avg=Avg('ease_factor')
    )['avg'] or 0

    return JsonResponse({
        'total_cards': total_cards,
        'studied': studied,
        'mastered': mastered,
        'average_ease': round(avg_ease, 2),
        'recent_sessions': session_data,
    })


# ---------------------------------------------------------------------------
# API — Export
# ---------------------------------------------------------------------------

def api_export(request):
    cards = Card.objects.select_related('category', 'deck').all()
    data = []
    for card in cards:
        data.append({
            'category': card.category.name,
            'deck': card.deck.name if card.deck else None,
            'question': card.question,
            'answer': card.answer,
            'rationale': card.rationale,
        })
    return JsonResponse({'cards': data}, safe=False)


# ---------------------------------------------------------------------------
# API — Quiz
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def api_quiz_answer(request, pk):
    question = get_object_or_404(QuizQuestion, pk=pk)
    data = json.loads(request.body)
    is_correct = data.get('is_correct', False)
    question.is_correct = is_correct
    question.save()

    if is_correct:
        quiz = question.quiz
        quiz.score = quiz.questions.filter(is_correct=True).count()
        quiz.save()

    return JsonResponse({'status': 'ok', 'is_correct': is_correct})


@csrf_exempt
@require_POST
def api_quiz_complete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.completed_at = timezone.now()
    quiz.score = quiz.questions.filter(is_correct=True).count()
    quiz.save()
    return JsonResponse({
        'status': 'ok',
        'score': quiz.score,
        'total': quiz.num_questions,
        'percentage': quiz.percentage,
    })


# ---------------------------------------------------------------------------
# API — Guide Section Toggle
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def api_toggle_guide_section(request, pk):
    section = get_object_or_404(GuideSection, pk=pk)
    progress, _ = GuideSectionProgress.objects.get_or_create(section=section)
    progress.completed = not progress.completed
    progress.completed_at = timezone.now() if progress.completed else None
    progress.save()
    return JsonResponse({
        'status': 'ok',
        'completed': progress.completed,
    })


# ---------------------------------------------------------------------------
# PWA
# ---------------------------------------------------------------------------

def manifest(request):
    data = {
        'name': 'NCLEX Prep',
        'short_name': 'Prep',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#0f172a',
        'theme_color': '#6366f1',
        'icons': [
            {
                'src': '/static/cards/icon-192.png',
                'sizes': '192x192',
                'type': 'image/png',
            },
            {
                'src': '/static/cards/icon-512.png',
                'sizes': '512x512',
                'type': 'image/png',
            },
        ],
    }
    return JsonResponse(data)


def service_worker(request):
    js = """
const CACHE_NAME = 'prep-v4';
const URLS_TO_CACHE = ['/'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(names =>
      Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
"""
    return HttpResponse(js, content_type='application/javascript')
