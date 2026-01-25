from django.urls import path
from main import views

urlpatterns = [
    path('search_questions/', views.search_questions),
    path('question_like/', views.question_like),
    path('answer_like/', views.answer_like),
    path('mark_answer/', views.mark_answer),
    path('centrifugo/token/', views.centrifugo_token, name='centrifugo_token'),
    path('toggle_theme/', views.toggle_theme),
]
