from django import forms

from plenosapp.models import Voting


class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ["title", "description", "videoUrl", "meeting"]