import json
import random
import markdown as md_lib
from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Count, Q, Avg

from .models import Card, Category, Deck, Progress, StudySession, Quiz, QuizQuestion, GuideSection, GuideSectionProgress
from .forms import CardForm, CategoryForm, ImportForm


# ── Helper ────────────────────────────────

def _get_streak():
    streak = 0
    d = date.today()
    while StudySession.objects.filter(date=d).exists():
        streak += 1
        d -= timedelta(days=1)
    return streak


def _get_global_stats():
    total_cards = Card.objects.count()
    studied = Progress.objects.filter(times_studied__gt=0).count()
    mastered = Progress.objects.filter(last_rating__gte=5, times_studied__gt=0).count()
    weak = Progress.objects.filter(last_rating__lte=1, times_studied__gt=0).count()
    today_session = StudySession.objects.filter(date=date.today()).first()
    return {
        'total_cards': total_cards,
        'studied': studied,
        'mastered': mastered,
        'weak': weak,
        'streak': _get_streak(),
        'today_studied': today_session.cards_studied if today_session else 0,
        'today_correct': today_session.cards_correct if today_session else 0,
        'accuracy': round(studied / total_cards * 100) if total_cards > 0 else 0,
    }


# ══════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════

def dashboard_view(request):
    stats = _get_global_stats()
    categories = Category.objects.filter(published=True).annotate(
        total=Count('cards'),
        studied_count=Count('cards__progress', filter=Q(cards__progress__times_studied__gt=0))
    )
    cat_progress = []
    for cat in categories:
        pct = round(cat.studied_count / cat.total * 100) if cat.total > 0 else 0
        cat_progress.append({
            'name': cat.name, 'icon': cat.icon, 'slug': cat.slug,
            'total': cat.total, 'studied': cat.studied_count, 'pct': pct,
            'exam_count': cat.decks.count(),
        })

    recent_quizzes = Quiz.objects.filter(completed_at__isnull=False).select_related('category')[:5]
    review_count = Progress.objects.filter(needs_review=True).count()

    return render(request, 'cards/dashboard.html', {
        'stats': stats,
        'categories': cat_progress,
        'recent_quizzes': recent_quizzes,
        'review_count': review_count,
    })


def study_view(request):
    categories = Category.objects.annotate(card_count=Count('cards')).filter(card_count__gt=0)
    # Build topics for the dropdown
    topics = []
    for gs in GuideSection.objects.select_related('deck__category').exclude(
        title__startswith='How to use'
    ).exclude(title__startswith='Best way').exclude(title__startswith='Fast Final'):
        card_count = gs.cards.count()
        if card_count > 0:
            topics.append({
                'id': gs.id,
                'title': gs.title,
                'card_count': card_count,
                'deck_name': gs.deck.name,
                'category_name': gs.deck.category.name,
            })
    return render(request, 'cards/study.html', {'categories': categories, 'topics': topics})


def manage_view(request):
    category_slug = request.GET.get('category', '')
    q = request.GET.get('q', '')

    cards = Card.objects.select_related('category').all()
    if category_slug:
        cards = cards.filter(category__slug=category_slug)
    if q:
        cards = cards.filter(Q(question__icontains=q) | Q(answer__icontains=q))

    categories = Category.objects.annotate(card_count=Count('cards'))
    return render(request, 'cards/manage.html', {
        'cards': cards,
        'categories': categories,
        'active_category': category_slug,
        'search_query': q,
        'import_form': ImportForm(),
    })


def card_create_view(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage')
    else:
        form = CardForm()
    return render(request, 'cards/card_form.html', {'form': form, 'title': 'Add Card'})


def card_edit_view(request, pk):
    card = get_object_or_404(Card, pk=pk)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('manage')
    else:
        form = CardForm(instance=card)
    return render(request, 'cards/card_form.html', {'form': form, 'card': card, 'title': 'Edit Card'})


def card_delete_view(request, pk):
    card = get_object_or_404(Card, pk=pk)
    if request.method == 'POST':
        card.delete()
        return redirect('manage')
    return render(request, 'cards/card_confirm_delete.html', {'card': card})


def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.slug = slugify(cat.name)
            cat.save()
            return redirect('manage')
    else:
        form = CategoryForm()
    return render(request, 'cards/category_form.html', {'form': form})


# ══════════════════════════════════════════
#  CATEGORY & EXAM HUB
# ══════════════════════════════════════════

def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    decks = category.decks.annotate(
        total=Count('cards'),
        studied_count=Count('cards__progress', filter=Q(cards__progress__times_studied__gt=0)),
    )

    deck_data = []
    for deck in decks:
        pct = round(deck.studied_count / deck.total * 100) if deck.total > 0 else 0
        guide_count = deck.guide_sections.count()
        deck_data.append({
            'id': deck.id,
            'name': deck.name,
            'slug': deck.slug,
            'total': deck.total,
            'studied': deck.studied_count,
            'pct': pct,
            'has_guide': guide_count > 0,
        })

    total_cards = Card.objects.filter(category=category).count()
    studied = Progress.objects.filter(card__category=category, times_studied__gt=0).count()
    cat_pct = round(studied / total_cards * 100) if total_cards > 0 else 0

    return render(request, 'cards/category_detail.html', {
        'category': category,
        'decks': deck_data,
        'total_cards': total_cards,
        'studied': studied,
        'cat_pct': cat_pct,
    })


def exam_detail_view(request, slug, deck_id):
    category = get_object_or_404(Category, slug=slug)
    deck = get_object_or_404(Deck, pk=deck_id, category=category)

    total = deck.cards.count()
    studied = Progress.objects.filter(card__deck=deck, times_studied__gt=0).count()
    mastered = Progress.objects.filter(card__deck=deck, last_rating__gte=5, times_studied__gt=0).count()
    weak = Progress.objects.filter(card__deck=deck, last_rating__lte=1, times_studied__gt=0).count()
    pct = round(studied / total * 100) if total > 0 else 0

    # Build topic sections
    topics = []
    sections = deck.guide_sections.exclude(
        title__startswith='How to use'
    ).exclude(
        title__startswith='Best way'
    ).exclude(
        title__startswith='Fast Final'
    )
    for s in sections:
        card_count = s.cards.count()
        s_studied = Progress.objects.filter(card__guide_section=s, times_studied__gt=0).count()
        s_pct = round(s_studied / card_count * 100) if card_count > 0 else 0
        topics.append({
            'id': s.id,
            'title': s.title,
            'card_count': card_count,
            'pct': s_pct,
        })

    return render(request, 'cards/exam_detail.html', {
        'category': category,
        'deck': deck,
        'total': total,
        'studied': studied,
        'mastered': mastered,
        'weak': weak,
        'pct': pct,
        'has_guide': deck.guide_sections.exists(),
        'topics': topics,
    })


def learn_view(request, slug, deck_id):
    category = get_object_or_404(Category, slug=slug)
    deck = get_object_or_404(Deck, pk=deck_id, category=category)
    sections = deck.guide_sections.all()

    # Ensure progress records exist
    for s in sections:
        GuideSectionProgress.objects.get_or_create(section=s)

    sections_data = []
    total = sections.count()
    completed = 0
    for s in sections:
        prog = s.progress if hasattr(s, 'progress') else None
        is_done = prog.completed if prog else False
        if is_done:
            completed += 1
        sections_data.append({
            'id': s.id,
            'title': s.title,
            'content_html': md_lib.markdown(s.content, extensions=['extra', 'nl2br']),
            'completed': is_done,
        })

    pct = round(completed / total * 100) if total > 0 else 0

    return render(request, 'cards/learn.html', {
        'category': category,
        'deck': deck,
        'sections': sections_data,
        'total': total,
        'completed': completed,
        'pct': pct,
    })


@require_POST
def api_toggle_guide_section(request, pk):
    section = get_object_or_404(GuideSection, pk=pk)
    prog, _ = GuideSectionProgress.objects.get_or_create(section=section)
    prog.completed = not prog.completed
    prog.completed_at = timezone.now() if prog.completed else None
    prog.save()
    return JsonResponse({'ok': True, 'completed': prog.completed})


# ══════════════════════════════════════════
#  REVISE
# ══════════════════════════════════════════

def revise_view(request):
    """Show all cards flagged for review."""
    review_cards = Card.objects.filter(
        progress__needs_review=True
    ).select_related('category', 'deck', 'guide_section')

    # Group by guide section
    sections = {}
    for card in review_cards:
        section_name = card.guide_section.title if card.guide_section else 'Uncategorized'
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(card)

    return render(request, 'cards/revise.html', {
        'sections': sections,
        'total': review_cards.count(),
    })


@require_POST
def api_clear_review(request, pk):
    """Remove a card from the review list."""
    card = get_object_or_404(Card, pk=pk)
    prog = Progress.objects.filter(card=card).first()
    if prog:
        prog.needs_review = False
        prog.save()
    return JsonResponse({'ok': True})


@require_POST
def api_section_revise(request, pk):
    """Flag all cards in a guide section for review."""
    section = get_object_or_404(GuideSection, pk=pk)
    cards = Card.objects.filter(guide_section=section)
    count = 0
    for card in cards:
        prog, _ = Progress.objects.get_or_create(card=card)
        prog.needs_review = True
        prog.save()
        count += 1
    return JsonResponse({'ok': True, 'count': count})


@require_POST
def api_section_unrevise(request, pk):
    """Clear review flag for all cards in a guide section."""
    section = get_object_or_404(GuideSection, pk=pk)
    Progress.objects.filter(card__guide_section=section, needs_review=True).update(needs_review=False)
    return JsonResponse({'ok': True})


# ══════════════════════════════════════════
#  QUIZ / TEST
# ══════════════════════════════════════════

def quiz_setup_view(request):
    topics = []
    for gs in GuideSection.objects.select_related('deck__category').exclude(
        title__startswith='How to use'
    ).exclude(title__startswith='Best way').exclude(title__startswith='Fast Final'):
        card_count = gs.cards.count()
        if card_count > 0:
            topics.append({'id': gs.id, 'title': gs.title, 'card_count': card_count})
    return render(request, 'cards/quiz_setup.html', {'topics': topics})


@require_POST
def quiz_start_view(request):
    """Create a new quiz and redirect to the quiz page."""
    num_questions = int(request.POST.get('num_questions', 10))
    time_limit = request.POST.get('time_limit', '')
    time_limit = int(time_limit) if time_limit else None

    cards = Card.objects.all()

    # Filter by selected sections (topics)
    section_ids = request.POST.getlist('sections')
    if section_ids:
        cards = cards.filter(guide_section_id__in=section_ids)

    # Legacy: filter by category/deck if passed
    category_slug = request.POST.get('category', '')
    if category_slug and category_slug != 'all':
        cards = cards.filter(category__slug=category_slug)
    deck_id = request.POST.get('deck', '')
    if deck_id:
        cards = cards.filter(deck_id=deck_id)

    card_list = list(cards)
    random.shuffle(card_list)
    card_list = card_list[:num_questions]

    if not card_list:
        return redirect('quiz_setup')

    quiz = Quiz.objects.create(
        category=None,
        num_questions=len(card_list),
        time_limit=time_limit,
    )

    for i, card in enumerate(card_list):
        QuizQuestion.objects.create(quiz=quiz, card=card, order=i + 1)

    return redirect('quiz_play', pk=quiz.pk)


def quiz_play_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if quiz.completed_at:
        return redirect('quiz_results', pk=quiz.pk)

    questions = quiz.questions.select_related('card__category').all()
    questions_data = [{
        'id': q.id,
        'order': q.order,
        'question': q.card.question,
        'answer': q.card.answer,
        'rationale': q.card.rationale,
        'categoryLabel': q.card.category.name,
        'categoryIcon': q.card.category.icon,
        'isCorrect': q.is_correct,
    } for q in questions]

    return render(request, 'cards/quiz_play.html', {
        'quiz': quiz,
        'questions_json': json.dumps(questions_data),
        'total': quiz.num_questions,
    })


@require_POST
def api_quiz_answer(request, pk):
    """Mark a single quiz question as correct or incorrect."""
    quiz = get_object_or_404(Quiz, pk=pk)
    body = json.loads(request.body)
    question_id = body.get('question_id')
    is_correct = body.get('is_correct')

    question = get_object_or_404(QuizQuestion, pk=question_id, quiz=quiz)
    question.is_correct = is_correct
    question.save()

    # Flag card for review if answered wrong
    prog, _ = Progress.objects.get_or_create(card=question.card)
    if not is_correct:
        prog.needs_review = True
        prog.save()
    elif is_correct and prog.needs_review:
        # Don't auto-clear from test — only clear from study mode rating ≥4
        pass

    answered = quiz.questions.filter(is_correct__isnull=False).count()
    correct = quiz.questions.filter(is_correct=True).count()

    return JsonResponse({
        'ok': True,
        'answered': answered,
        'correct': correct,
        'total': quiz.num_questions,
    })


@require_POST
def api_quiz_complete(request, pk):
    """Mark quiz as completed, calculate score."""
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.score = quiz.questions.filter(is_correct=True).count()
    quiz.completed_at = timezone.now()
    quiz.save()

    # Update study session
    today_session, _ = StudySession.objects.get_or_create(date=date.today())
    today_session.cards_studied += quiz.num_questions
    today_session.cards_correct += quiz.score
    today_session.save()

    return JsonResponse({
        'ok': True,
        'score': quiz.score,
        'total': quiz.num_questions,
        'percentage': quiz.percentage,
        'duration': quiz.duration_display,
    })


def quiz_results_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.select_related('card__category').all()
    return render(request, 'cards/quiz_results.html', {
        'quiz': quiz,
        'questions': questions,
    })


def quiz_history_view(request):
    quizzes = Quiz.objects.filter(completed_at__isnull=False).select_related('category')
    return render(request, 'cards/quiz_history.html', {'quizzes': quizzes})


# ══════════════════════════════════════════
#  API: Cards & Progress (existing)
# ══════════════════════════════════════════

def api_cards(request):
    category = request.GET.get('category', '')
    deck_id = request.GET.get('deck', '')
    section_id = request.GET.get('section', '')
    cards = Card.objects.select_related('category').all()
    if category and category != 'all':
        cards = cards.filter(category__slug=category)
    if deck_id:
        cards = cards.filter(deck_id=deck_id)
    if section_id:
        section_ids = [s.strip() for s in section_id.split(',') if s.strip()]
        if len(section_ids) == 1:
            cards = cards.filter(guide_section_id=section_ids[0])
        elif len(section_ids) > 1:
            cards = cards.filter(guide_section_id__in=section_ids)

    data = []
    for c in cards:
        prog = Progress.objects.filter(card=c).first()
        data.append({
            'id': c.id,
            'category': c.category.slug,
            'categoryLabel': c.category.name,
            'categoryIcon': c.category.icon,
            'question': c.question,
            'answer': c.answer,
            'rationale': c.rationale,
            'progress': {
                'easeFactor': prog.ease_factor if prog else 2.5,
                'interval': prog.interval if prog else 0,
                'repetitions': prog.repetitions if prog else 0,
                'timesStudied': prog.times_studied if prog else 0,
                'lastRating': prog.last_rating if prog else 0,
                'nextReview': str(prog.next_review) if prog and prog.next_review else None,
            }
        })

    return JsonResponse({'cards': data, 'total': len(data)})


@require_POST
def api_rate_card(request, pk):
    card = get_object_or_404(Card, pk=pk)
    body = json.loads(request.body)
    rating = int(body.get('rating', 3))

    prog, _ = Progress.objects.get_or_create(card=card)
    prog.times_studied += 1
    prog.last_rating = rating

    # SM-2 algorithm
    if rating >= 3:
        if prog.repetitions == 0:
            prog.interval = 1
        elif prog.repetitions == 1:
            prog.interval = 6
        else:
            prog.interval = round(prog.interval * prog.ease_factor)
        prog.repetitions += 1
    else:
        prog.repetitions = 0
        prog.interval = 1

    prog.ease_factor = max(1.3,
        prog.ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
    )
    prog.next_review = date.today() + timedelta(days=prog.interval)

    # Flag for review if rated hard or OK
    if rating <= 3:
        prog.needs_review = True
    elif rating >= 4:
        prog.needs_review = False

    prog.save()

    # Update daily session
    today = date.today()
    session, _ = StudySession.objects.get_or_create(date=today)
    session.cards_studied += 1
    if rating >= 3:
        session.cards_correct += 1
    session.save()

    return JsonResponse({
        'ok': True,
        'progress': {
            'easeFactor': prog.ease_factor,
            'interval': prog.interval,
            'repetitions': prog.repetitions,
            'timesStudied': prog.times_studied,
            'lastRating': prog.last_rating,
            'nextReview': str(prog.next_review),
        }
    })


def api_stats(request):
    total_cards = Card.objects.count()
    studied = Progress.objects.filter(times_studied__gt=0).count()
    mastered = Progress.objects.filter(last_rating__gte=5, times_studied__gt=0).count()
    weak = Progress.objects.filter(last_rating__lte=1, times_studied__gt=0).count()

    # Streak
    streak = 0
    d = date.today()
    while StudySession.objects.filter(date=d).exists():
        streak += 1
        d -= timedelta(days=1)

    # Category breakdown
    cats = []
    for cat in Category.objects.annotate(total=Count('cards')):
        cat_studied = Progress.objects.filter(
            card__category=cat, times_studied__gt=0
        ).count()
        cats.append({
            'name': f'{cat.icon} {cat.name}',
            'slug': cat.slug,
            'total': cat.total,
            'studied': cat_studied,
            'pct': round(cat_studied / cat.total * 100) if cat.total > 0 else 0,
        })

    # Today's session
    today_session = StudySession.objects.filter(date=date.today()).first()

    return JsonResponse({
        'totalCards': total_cards,
        'studied': studied,
        'mastered': mastered,
        'weak': weak,
        'streak': streak,
        'categories': cats,
        'today': {
            'studied': today_session.cards_studied if today_session else 0,
            'correct': today_session.cards_correct if today_session else 0,
        }
    })


# ── Import / Export ───────────────────────

def api_export(request):
    cards = Card.objects.select_related('category').all()
    data = {
        'version': 1,
        'exported': str(date.today()),
        'categories': list(Category.objects.values('name', 'slug', 'icon')),
        'cards': [{
            'category_slug': c.category.slug,
            'question': c.question,
            'answer': c.answer,
            'rationale': c.rationale,
        } for c in cards]
    }

    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="prep-export-{date.today()}.json"'
    return response


def import_cards_view(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                data = json.load(request.FILES['file'])
                imported = 0

                # Create categories
                cat_map = {}
                for cat_data in data.get('categories', []):
                    cat, _ = Category.objects.get_or_create(
                        slug=cat_data['slug'],
                        defaults={'name': cat_data['name'], 'icon': cat_data.get('icon', '📚')}
                    )
                    cat_map[cat_data['slug']] = cat

                # Create cards
                for card_data in data.get('cards', []):
                    slug = card_data['category_slug']
                    if slug not in cat_map:
                        continue
                    _, created = Card.objects.get_or_create(
                        question=card_data['question'],
                        defaults={
                            'category': cat_map[slug],
                            'answer': card_data['answer'],
                            'rationale': card_data.get('rationale', ''),
                        }
                    )
                    if created:
                        imported += 1

                return redirect('manage')
            except (json.JSONDecodeError, KeyError):
                form.add_error('file', 'Invalid JSON file format.')

    return redirect('manage')


# ── PWA ───────────────────────────────────

def manifest(request):
    data = {
        "name": "Prep — NCLEX Flashcards",
        "short_name": "Prep",
        "description": "Study for NCLEX with smart flashcards, spaced repetition & audio",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f0fdfa",
        "theme_color": "#0d9488",
        "orientation": "portrait-primary",
        "categories": ["education", "medical"],
        "icons": [
            {
                "src": "/static/cards/icons/icon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any"
            },
            {
                "src": "/static/cards/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/cards/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return JsonResponse(data)


def service_worker(request):
    sw_js = """const CACHE_NAME='prep-v4';
const ASSETS=['/','/static/cards/css/styles.css','/static/cards/js/app.js','/static/cards/icons/icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(ASSETS)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).then(r=>{if(r.ok){const c=r.clone();caches.open(CACHE_NAME).then(cache=>cache.put(e.request,c))}return r}).catch(()=>caches.match(e.request)))});"""
    return HttpResponse(sw_js, content_type='application/javascript')


def cron(request):
    return HttpResponse('hello')

