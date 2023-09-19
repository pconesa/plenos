from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import *

# Create your views here.
from django.http import HttpResponse

# custom 404 view
def custom_404(request, exception):
    return render(request, 'plenosapp/404.html', status=404)

def index(request):
    context = {
        'towns': Town.objects.all(),
        'meetings': Meeting.objects.all(),
        'politicians': Politician.objects.all(),

    }

    return render(request, 'plenosapp/index.html', context)

def template(request):
    return render(request, 'plenosapp/template.html')

def party(request, party_id):
    return HttpResponse("You're looking at party %s." % party_id)

def town(request, town_id):
    town = get_object_or_404(Town, pk=town_id)
    jobs = Job.objects.filter(town=town_id, end__isnull=True)
    meetings = Meeting.objects.filter(town_id=town_id)
    votings = Voting.objects.filter(meeting__town=town_id)
    return render(request, 'plenosapp/town.html',
                  {"town":town,
                   "jobs":jobs,
                   "meetings":meetings,
                   "votings":votings})

def voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    return render(request, 'plenosapp/voting.html',
                  {"voting":voting})

def meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    votings = Voting.objects.filter(meeting_id=meeting_id)
    return render(request, 'plenosapp/meeting.html',
                  {"meeting":meeting,
                   "votings":votings})

def search(request):
    jobs = get_list_or_404(Job)
    return render(request, 'plenosapp/search.html', {"jobs":jobs})

def politician(request, politician_id):
    return HttpResponse("You're looking at the politician %s." % politician_id)

def contribute(request):
    """ Returns the response for the contribution page  """
    return render(request, 'plenosapp/contribute.html')