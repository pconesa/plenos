import datetime

from django.db import models
from django.urls import reverse
from plenos import settings

from .utils import extractYoutubeStart, extractYoutubeId, extractVimeoId, extractVimeoStart
from django.db.models.signals import post_save
from .facebook import postOnFacebook

# Create your models here.
class Party(models.Model):
    """ Political party """
    name = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return f'{self.name}'

class Town(models.Model):
    """ Town """
    name = models.CharField(max_length=300)
    location = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name}'

class Politician(models.Model):
    """ Politician """
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    picture = models.ImageField(verbose_name="Foto cuadrada", upload_to='politicians/', blank=True, null=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.surname}'

class Charge(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Job(models.Model):
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    charge = models.ForeignKey(Charge, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.politician}: {self.start}->{self.end}: {self.charge.name}, {self.party.name}, {self.town.name}'

class Meeting(models.Model):
    """Plenos """

    class Meta:
        ordering = ['-day']

    day = models.DateField()
    url = models.URLField(verbose_name="Enlace a YouTube/Vimeo video")
    town = models.ForeignKey(Town, on_delete=models.CASCADE)

    def isVimeo(self):
        return "vimeo" in self.url

    def videoId(self):
        if self.isVimeo():
            return extractVimeoId(self.url)
        else:
            return extractYoutubeId(self.url)

    def videoStart(self):
        if self.isVimeo():
            return extractVimeoStart(self.url)
        else:
            return extractYoutubeStart(self.url)

    def __str__(self):
        return f'{self.town} Día {self.day}'

class Voting(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=2000)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    maxVotes = models.IntegerField(verbose_name="Número de concejales", default=13)
    videoUrl = models.URLField(verbose_name="YouTube video url (conteniendo v=) en el momento de la votacion", null=True)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            postOnFacebook("Hay una nueva votación del pleno de %s.\n%s:\n%s\n\n¡Échala un ojo aquí!-->%s" %
                           (instance.meeting,
                            instance.title, instance.description,
                            settings.HOST + reverse('voting', urlconf='plenosapp.urls', kwargs={'voting_id': instance.id})
                            ))

    def isVimeo(self):
        return "vimeo" in self.videoUrl

    def videoId(self):
        if self.isVimeo():
            return extractVimeoId(self.videoUrl)
        else:
            return extractYoutubeId(self.videoUrl)

    def videoStart(self):
        if self.isVimeo():
            return extractVimeoStart(self.videoUrl)
        else:
            return extractYoutubeStart(self.videoUrl)

    def getResults(self):

        results = [[True, 0,0,0],[False,0,0,0],[None,0,0,0]] # A favor, en contra, abstenciones
        from django.db.models import Count

        for vote in Vote.objects.filter(voting_id=self.id).order_by("positive").values("positive")\
                .annotate(num_votes=Count("positive")):
            lastValue=vote['positive']
            num_votes=vote['num_votes']
            pos = 0 if lastValue else 2 if lastValue is None else 1
            results[pos] =  [lastValue, 0,0, num_votes]

        fromValue = 0.
        for value in results:
            percentage = round(100 * value[3] / self.maxVotes, 2)
            value[1]=fromValue
            fromValue +=percentage
            value[2]=fromValue

        # Add the nones
        results[2]= [None, fromValue, 100, round((100-fromValue)/(100/self.maxVotes))]

        return results

    def __str__(self):
        return f'{self.title} - {self.meeting}'

# Register binding to "post_save" of voting
post_save.connect(Voting.post_create, sender=Voting)


class Vote(models.Model):
    positive = models.BooleanField(null=True)
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.positive} - {self.job.politician} - {self.voting}'

class Resource(models.Model):
    name = models.CharField(null=False, max_length=100)
    url = models.URLField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, blank=True, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, blank=True, null=True)

    def finalURL(self):
        return self.url if self.url else self.file.url

    def __str__(self):
        fk = self.voting or self.meeting
        return f'{self.name}-{fk}'


# Politician analysis code
class VotingAnalysis:
    def __init__(self, job:Job):
        self.politician = job.politician
        self.town = job.town

        """ This will have the following structure:
        { voting: [ politicianVote, {
                    party: [true, false, None, Max]}
        """
        self._analysis = dict() # Key is the voting id
        self.similarity = []

        endDate= datetime.datetime.now() if job.end is None else job.end
        # For each voting in the town
        for vote in Vote.objects.filter(job__town=self.town, voting__meeting__day__gte=job.start, voting__meeting__day__lte=endDate ):
            self.registerVote(vote)

        # Summarize
        self.summarize()

    def getAnalysis(self):
        return self._analysis

    def getVotingItem(self, voting:Voting):
        item =  self._analysis.get(voting, None)

        if item is None:
            item = [None, {}]
            self._analysis[voting]= item

        return item

    def getPartyCounter(self, votingItem, party):

        votingItemParties = votingItem[1]
        partyCounter = votingItemParties.get(party,None)
        if partyCounter is None:
            partyCounter = [0,0,0,None]
            votingItemParties[party] = partyCounter
        return partyCounter

    def registerVote(self, vote:Vote):

        voting = self.getVotingItem(vote.voting)

        # Annotate the vote of the politician
        if vote.job.politician == self.politician:
            voting[0]=vote.positive

        # Add the vote to the party counters
        partyCounter = self.getPartyCounter(voting, vote.job.party)

        if vote.positive == True:
            partyCounter[0]+=1
        elif vote.positive == False:
            partyCounter[1] += 1
        else:
            partyCounter[2] += 1

    def summarize(self):

        for voting, votingItem in self._analysis.items():

            for index, (party, partyCounter) in enumerate(votingItem[1].items()):
                idx = getMaxIndex(partyCounter[:-1])
                partyFinalVote = True if idx==0 else (False if idx==1 else None)
                partyCounter[3] = partyFinalVote
                self.annotateSimilarity(index, partyFinalVote==votingItem[0])


        self.annotatePercentage()

    def annotatePercentage(self):
        count = len(self._analysis)
        for similarity in self.similarity:
            similarity[1] = int(100*similarity[0]/count)

    def annotateSimilarity(self, index, matches):

        if len(self.similarity)==index:
            self.similarity.append([0,0])

        if matches:
            self.similarity[index][0] += 1

    def getSimilarity(self):
        """ Returns the similarity in votes of the politician with other parties"""
        self.similarity

def getMaxIndex(l):

    # Finding maximum element
    m = max(l)

    # iterating over the list like index,
    # item pair
    for i, j in enumerate(l):

        if j == m:
            return i
