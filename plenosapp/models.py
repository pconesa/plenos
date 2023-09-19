from django.db import models


# This may go somewhere else
from urllib.parse import parse_qs, urlparse

def extractYoutubeId(url):
    return extractGetParamFromURL(url, 'v')

def extractYoutubeStart(url):
    return extractGetParamFromURL(url, 't', default="0")

def extractGetParamFromURL(url, paramName, default=""):
    return parse_qs(urlparse(url).query).get(paramName,[default])[0]

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

    day = models.DateField()
    url = models.URLField(verbose_name="Youtube video url conteniendo 'v='")
    town = models.ForeignKey(Town, on_delete=models.CASCADE)

    def youtubeId(self):
        return extractYoutubeId(self.url)

    def youtubeStart(self):
        return extractYoutubeStart(self.url)

    def __str__(self):
        return f'{self.town} Día {self.day}'

class Voting(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=2000)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    maxVotes = models.IntegerField(verbose_name="Número de concejales", default=13)
    videoUrl = models.URLField(verbose_name="Youtube video url (conteniendo v=) en el momento de la votacion", null=True)

    def youtubeId(self):
        return extractYoutubeId(self.videoUrl)

    def youtubeStart(self):
        return extractYoutubeStart(self.videoUrl)

    def getResults(self):

        results = {}
        from django.db.models import Count

        fromValue = 0.

        for vote in Vote.objects.filter(voting_id=self.id).order_by("positive").values("positive")\
                .annotate(num_votes=Count("positive")):
            num_votes=vote['num_votes']
            percentage= round(100 *num_votes/self.maxVotes, 2)
            results[vote['positive']] =  (fromValue, fromValue +percentage, num_votes)
            fromValue +=percentage

        # Add the nones
        results[None]= (fromValue, 100, round((100-fromValue)/(100/self.maxVotes)))


        return results

    def __str__(self):
        return f'{self.title} - {self.meeting}'

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

    def __str__(self):
        fk = self.voting or self.meeting
        return f'{self.name}-{fk}'