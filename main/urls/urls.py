from django.urls import path
from main import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
    path('hot/', views.HotQuestionsPage.as_view(), name='hot_questions'),
    path('tag/<str:tag>/', views.TagePage.as_view(), name='tag'),
    path('question/<int:id>/', views.QuestionPage.as_view(), name='question'),
    path('ask/', views.AskPage.as_view(), name='ask'),
    path('profile/edit/', views.SettingsPage.as_view(), name='settings'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.RegistrationPage.as_view(), name='django_registration_register'),
    path('registration/closed/', TemplateView.as_view(
        template_name='django_registration/registration_closed.html',
        extra_context=views.create_base_context(),
    ), name='django_registration_disallowed'),
    path('registration/complete/', TemplateView.as_view(
        template_name='django_registration/registration_complete.html',
        extra_context=views.create_base_context(),
    ), name='django_registration_complete'),
]
