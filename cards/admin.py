from django.contrib import admin
from .models import Category, Deck, Card, Progress, StudySession, Quiz, QuizQuestion, GuideSection, GuideSectionProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'slug', 'published', 'is_default', 'card_count']
    prepopulated_fields = {'slug': ('name',)}

    def card_count(self, obj):
        return obj.cards.count()


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'card_count']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('name',)}

    def card_count(self, obj):
        return obj.cards.count()


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['short_question', 'category', 'deck', 'is_default', 'created_at']
    list_filter = ['category', 'deck', 'is_default']
    search_fields = ['question', 'answer']

    def short_question(self, obj):
        return obj.question[:80]


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['card', 'times_studied', 'last_rating', 'next_review', 'ease_factor']
    list_filter = ['last_rating']


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'cards_studied', 'cards_correct']


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    readonly_fields = ['card', 'order', 'is_correct']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'num_questions', 'score', 'percentage', 'duration_display', 'started_at']
    list_filter = ['category']
    inlines = [QuizQuestionInline]

    def percentage(self, obj):
        return f'{obj.percentage}%'


@admin.register(GuideSection)
class GuideSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'deck', 'order']
    list_filter = ['deck__category', 'deck']
    ordering = ['deck', 'order']
