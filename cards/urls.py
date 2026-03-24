from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    # Category & Exam Hub
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('category/<slug:slug>/exam/<int:deck_id>/', views.exam_detail_view, name='exam_detail'),
    path('category/<slug:slug>/exam/<int:deck_id>/learn/', views.learn_view, name='learn'),
    # Study
    path('study/', views.study_view, name='study'),
    # Quiz
    path('test/', views.quiz_setup_view, name='quiz_setup'),
    path('test/start/', views.quiz_start_view, name='quiz_start'),
    path('test/<int:pk>/', views.quiz_play_view, name='quiz_play'),
    path('test/<int:pk>/results/', views.quiz_results_view, name='quiz_results'),
    path('test/history/', views.quiz_history_view, name='quiz_history'),
    # Card Management
    path('manage/', views.manage_view, name='manage'),
    path('manage/add/', views.card_create_view, name='card_create'),
    path('manage/<int:pk>/edit/', views.card_edit_view, name='card_edit'),
    path('manage/<int:pk>/delete/', views.card_delete_view, name='card_delete'),
    path('manage/category/add/', views.category_create_view, name='category_create'),
    path('manage/import/', views.import_cards_view, name='import_cards'),
    # API
    path('api/cards/', views.api_cards, name='api_cards'),
    path('api/cards/<int:pk>/rate/', views.api_rate_card, name='api_rate_card'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/export/', views.api_export, name='api_export'),
    path('api/quiz/<int:pk>/answer/', views.api_quiz_answer, name='api_quiz_answer'),
    path('api/quiz/<int:pk>/complete/', views.api_quiz_complete, name='api_quiz_complete'),
    path('api/guide/<int:pk>/toggle/', views.api_toggle_guide_section, name='api_toggle_guide'),
    # PWA
    path('manifest.json', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service_worker'),
]
