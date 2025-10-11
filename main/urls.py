from django.urls import path
from main import views
from django.contrib.auth import views as auth_views
from django_registration.backends.one_step import views as reg_views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.index_page, name='index'),
    path('question/<int:id>/', views.question_page, name='question'),
    path('hot/', views.hot_questions_page, name='hot_questions'),
    path('ask/', views.ask_page, name='ask'),
    path('tag/<str:tag>/', views.tag_page, name='tag'),
    path('settings/', views.settings_page, name='settings'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', reg_views.RegistrationView.as_view(
        template_name='django_registration/registration_form.html',
        extra_context=views.create_base_context(),
    ), name='django_registration_register'),
    path('registration/closed/', TemplateView.as_view(
        template_name='django_registration/registration_closed.html',
        extra_context=views.create_base_context(),
    ), name='django_registration_disallowed'),
    path('registration/complete/', TemplateView.as_view(
        template_name='django_registration/registration_complete.html',
        extra_context=views.create_base_context(),
    ), name='django_registration_complete'),
]
