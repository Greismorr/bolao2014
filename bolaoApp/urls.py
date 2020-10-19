from django.urls import path
from . import views

urlpatterns = [
    path('', views.load_index, name='index'),
    path('login/', views.login_page, name='login'),
    path('registrar/', views.sign_up, name='registrar'),
    path('logout/', views.logout_page, name='logout'),
    path('partidas/', views.load_games, name='partidas'),
    path('ranking/', views.load_ranking, name='ranking'),
    path('apostar/', views.load_bet_form, name='apostar'),
]