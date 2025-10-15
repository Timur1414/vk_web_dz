from django.urls import path, include

urlpatterns = [
    path('', include('main.urls.urls')),
    path('api/', include('main.urls.api')),
]
