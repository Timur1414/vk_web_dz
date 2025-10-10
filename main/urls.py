from django.urls import path, include
from main import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index_page, name='index'),
    path('question/<int:id>/', views.question_page, name='question'),
    path('hot/', views.hot_questions_page, name='hot_questions'),
    path('ask/', views.ask_page, name='ask'),
    path('tag/<str:tag>/', views.tag_page, name='tag'),
    path('settings/', views.settings_page, name='settings'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', extra_context=views.create_base_context_for_login()), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', include('django_registration.backends.one_step.urls')),
]