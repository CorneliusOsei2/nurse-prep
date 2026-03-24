from django.contrib import admin
from .models import (
    Category, Deck, GuideSection, Card, Progress,
    StudySession, Quiz, QuizQuestion, GuideSectionProgress,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'slug', 'icon', 'card_count']
    prepopulated_fields = {'slug': ('name',)}

    def card_count(self, obj):
        return obj.cards.count()
    card_count.short_description = 'Cards'


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'card_count', 'order']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('name',)}

    def card_count(self, obj):
        return obj.cards.count()
    card_count.short_description = 'Cards'


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'category', 'deck', 'created_at']
    list_filter = ['category', 'deck']

    def question_short(self, obj):
        return obj.question[:80]
    question_short.short_description = 'Question'


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['card', 'ease_factor', 'interval', 'repetitions', 'next_review']


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'cards_studied', 'cards_correct']


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    readonly_fields = ['card', 'order', 'is_correct']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'num_questions', 'score', 'started_at', 'completed_at']
    inlines = [QuizQuestionInline]


@admin.register(GuideSection)
class GuideSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'deck', 'order']
    list_filter = ['deck']


@admin.register(GuideSectionProgress)
class GuideSectionProgressAdmin(admin.ModelAdmin):
    list_display = ['section', 'completed', 'completed_at']
