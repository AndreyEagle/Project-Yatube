from django.urls import path
from . import views

app_name = 'posts'
app_name = 'about'
app_name = 'core'

urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
