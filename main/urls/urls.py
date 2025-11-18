from django.urls import path
from main import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
    path('hot/', views.HotQuestionsPage.as_view(), name='hot_questions'),
    path('tag/<str:tag>/', views.TagPage.as_view(), name='tag'),
    path('question/<int:id>/', views.QuestionPage.as_view(), name='question'),
    path('ask/', views.AskPage.as_view(), name='ask'),
    path('profile/edit/', views.SettingsPage.as_view(), name='settings'),
    path('profile/<int:id>/', views.ProfilePage.as_view(), name='profile'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.RegistrationPage.as_view(), name='django_registration_register'),
    path('registration/closed/', views.ClosedRegistrationPage.as_view(), name='django_registration_disallowed'),
    path('password_change/', views.PasswordChangePage.as_view(), name='password_change'),
]
