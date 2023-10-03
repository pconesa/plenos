
from django.db import models
from django.urls import reverse
from plenos import settings

from .utils import extractYoutubeStart, extractYoutubeId
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
    videoUrl = models.URLField(verbose_name="YouTube video url (conteniendo v=) en el momento de la votacion", null=True)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            postOnFacebook("Hay una nueva votación del pleno de %s.\n%s:\n%s\n\n¡Échala un ojo aquí!-->%s" %
                           (instance.meeting,
                            instance.title, instance.description,
                            settings.HOST + reverse('voting', urlconf='plenosapp.urls', kwargs={'voting_id': instance.id})
                            ))

    def youtubeId(self):
        return extractYoutubeId(self.videoUrl)

    def youtubeStart(self):
        return extractYoutubeStart(self.videoUrl)

    def getResults(self):

        results = [[True, 0,0,0],[False,0,0,0],[None,0,0,0]] # A favor, en contra, abstenciones
        from django.db.models import Count

        lastValue=None

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