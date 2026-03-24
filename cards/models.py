from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📚')
    is_default = models.BooleanField(default=False)
    published = models.BooleanField(default=False, help_text='Show on homepage')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return f'{self.icon} {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Deck(models.Model):
    """An exam/deck within a category (e.g., Exam 1, Exam 2)."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    order = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['category', 'order']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f'{self.category.name} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Card(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cards')
    deck = models.ForeignKey(Deck, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    guide_section = models.ForeignKey('GuideSection', on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    question = models.TextField()
    answer = models.TextField()
    rationale = models.TextField(blank=True, default='')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'id']

    def __str__(self):
        return self.question[:80]


class Progress(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name='progress')
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    times_studied = models.IntegerField(default=0)
    last_rating = models.IntegerField(default=0)
    next_review = models.DateField(null=True, blank=True)
    needs_review = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'progress'

    def __str__(self):
        return f'Progress for card {self.card_id}'


class StudySession(models.Model):
    """Tracks daily study stats and streak."""
    date = models.DateField(unique=True)
    cards_studied = models.IntegerField(default=0)
    cards_correct = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.date}: {self.cards_studied} studied'


class Quiz(models.Model):
    """A timed quiz/test attempt."""
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='Null means all categories'
    )
    num_questions = models.IntegerField()
    time_limit = models.IntegerField(null=True, blank=True, help_text='Time limit in minutes')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'quizzes'
        ordering = ['-started_at']

    def __str__(self):
        cat = self.category.name if self.category else 'All'
        return f'Quiz ({cat}) — {self.score}/{self.num_questions}'

    @property
    def percentage(self):
        return round(self.score / self.num_questions * 100) if self.num_questions > 0 else 0

    @property
    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    @property
    def duration_display(self):
        secs = self.duration_seconds
        if secs is None:
            return '—'
        mins, s = divmod(secs, 60)
        return f'{mins}m {s:02d}s'


class QuizQuestion(models.Model):
    """An individual question within a quiz."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        status = '✅' if self.is_correct else ('❌' if self.is_correct is False else '⬜')
        return f'{status} Q{self.order}: {self.card.question[:50]}'


class GuideSection(models.Model):
    """A section of a study guide for a deck/exam."""
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='guide_sections')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['deck', 'order']

    def __str__(self):
        return f'{self.deck} — {self.title}'


class GuideSectionProgress(models.Model):
    """Tracks whether a user has completed a guide section."""
    section = models.OneToOneField(GuideSection, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{"✅" if self.completed else "⬜"} {self.section.title}'
