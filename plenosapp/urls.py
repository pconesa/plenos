from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Partidos
    path('parties/', views.parties, name='parties'),
    path('<int:party_id>/', views.party, name='party'),
    #Localidades
    path('town/<int:town_id>', views.town, name='town'),
    path('towns/', views.towns, name='towns'),

    # Politicos
    path('<int:politician_id>/vote/', views.politician, name='politician'),

    # Plenos y votaciones
    path('voting/<int:voting_id>', views.voting, name='voting'),
    path('meeting/<int:meeting_id>', views.meeting, name='meeting'),

    path('contribute/', views.contribute, name='contribute'),

]


