from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django import forms

from .forms import VotingForm
from .models import *

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


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
    votings = Voting.objects.filter(meeting__town=town_id).order_by("-id")[:5]
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
    politician = get_object_or_404(Politician, pk=politician_id)
    currentjob= get_object_or_404(Job.objects.filter(politician=politician, end__isnull=True))
    analysis = VotingAnalysis(currentjob)
    return render(request, 'plenosapp/politician.html',
                  {"politician":politician,
                   "analysis": analysis
                   })

def contribute(request):
    """ Returns the response for the contribution page  """
    return render(request, 'plenosapp/contribute.html')


# Securized pages
@login_required
def editvoting(request, voting_id):

    if voting_id:
        voting = get_object_or_404(Voting, pk=voting_id)
    else:
        # New voting
        voting = Voting()

    form = VotingForm(request.POST or None, instance=voting)

    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect("/editvotes/")

    return render(request, 'plenosapp/editvoting.html',
                  {"form":form,
                   })
