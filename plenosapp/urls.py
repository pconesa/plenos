from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('template/', views.template, name='template'),
    # Busqueda
    path('search/', views.search, name='search'),

    # Partido
    path('<int:party_id>/', views.party, name='party'),

    # Localidad
    path('town/<int:town_id>', views.town, name='town'),

    # Politico
    path('politician/<int:politician_id>', views.politician, name='politician'),

    # Plenos y votaciones
    path('voting/<int:voting_id>', views.voting, name='voting'),
    path('meeting/<int:meeting_id>', views.meeting, name='meeting'),

    # Colabora
    path('contribute/', views.contribute, name='contribute'),

    # Securized pages
    path("accounts/login/", auth_views.LoginView.as_view()),
    path('edit/voting/<int:voting_id>', views.editvoting, name='editvoting'),

]


